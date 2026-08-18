import cv2
import numpy as np
import urllib.request
from flask import Flask, jsonify, request, Response
import logging
import threading
import time
from vision_detector import VisionDetector

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Global states
detector = VisionDetector(log_func=logging.info)
current_frame = None
latest_result_center = None
camera_url = ""
stream_running = False

def fetch_image(url):
    try:
        req = urllib.request.urlopen(url, timeout=2)
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        img = cv2.imdecode(arr, -1)
        return img
    except Exception as e:
        logging.error(f"Error fetching image: {e}")
        return None

def background_stream():
    global current_frame, latest_result_center
    while stream_running:
        if camera_url:
            img = fetch_image(camera_url)
            if img is not None:
                center, processed_img = detector.nozzleDetection(img)
                latest_result_center = center
                
                # Encode the frame in JPEG format
                ret, buffer = cv2.imencode('.jpg', processed_img)
                if ret:
                    current_frame = buffer.tobytes()
        time.sleep(0.1) # 10 FPS to save CPU

def generate_mjpeg():
    global current_frame
    while True:
        if current_frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + current_frame + b'\r\n')
        time.sleep(0.1)

@app.route('/stream', methods=['GET'])
def stream():
    return Response(generate_mjpeg(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detect', methods=['GET'])
def detect_nozzle():
    global camera_url, stream_running
    cam = request.args.get('camera_url')
    
    if not cam:
        return jsonify({"status": "error", "message": "Missing camera_url"}), 400
        
    if camera_url != cam:
        camera_url = cam
        
    # Start stream thread if not running
    if not stream_running:
        stream_running = True
        threading.Thread(target=background_stream, daemon=True).start()
        
    # Wait up to 2 seconds for a frame
    for _ in range(20):
        if latest_result_center is not None:
            return jsonify({
                "status": "ok",
                "x": latest_result_center[0],
                "y": latest_result_center[1]
            })
        time.sleep(0.1)
        
    return jsonify({"status": "not_found", "message": "Nozzle not detected"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8085, threaded=True)

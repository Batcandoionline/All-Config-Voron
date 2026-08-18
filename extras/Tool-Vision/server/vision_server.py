import cv2
import numpy as np
import copy
import urllib.request
from flask import Flask, jsonify, request
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

class NozzleDetector:
    def __init__(self):
        # Setup OpenCV SimpleBlobDetector parameters just like kTAMV
        self.stdParams = cv2.SimpleBlobDetector_Params()
        self.stdParams.minThreshold = 1
        self.stdParams.maxThreshold = 50
        self.stdParams.thresholdStep = 1
        self.stdParams.filterByArea = True
        self.stdParams.minArea = 400
        self.stdParams.maxArea = 900
        self.stdParams.filterByCircularity = True
        self.stdParams.minCircularity = 0.8
        self.stdParams.maxCircularity = 1
        self.stdParams.filterByConvexity = True
        self.stdParams.minConvexity = 0.3
        self.stdParams.maxConvexity = 1
        self.stdParams.filterByInertia = True
        self.stdParams.minInertiaRatio = 0.3
        
        self.detector = cv2.SimpleBlobDetector_create(self.stdParams)

    def fetch_image(self, url):
        try:
            req = urllib.request.urlopen(url, timeout=2)
            arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
            img = cv2.imdecode(arr, -1)
            return img
        except Exception as e:
            logging.error(f"Error fetching image: {e}")
            return None

    def preprocess(self, img):
        # algorithm 1 from kTAMV
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_TRIANGLE)
        blurred = cv2.GaussianBlur(thresh, (7, 7), 6)
        return cv2.cvtColor(blurred, cv2.COLOR_GRAY2BGR)

    def detect(self, img):
        processed = self.preprocess(img)
        keypoints = self.detector.detect(processed)
        if not keypoints:
            return None
            
        # Find closest to center (320, 240)
        target = np.array([320, 240])
        closest_kp = min(keypoints, key=lambda kp: np.linalg.norm(np.array(kp.pt) - target))
        x, y = int(closest_kp.pt[0]), int(closest_kp.pt[1])
        return (x, y)

detector = NozzleDetector()

@app.route('/detect', methods=['GET'])
def detect_nozzle():
    camera_url = request.args.get('camera_url')
    if not camera_url:
        return jsonify({"status": "error", "message": "Missing camera_url"}), 400
        
    img = detector.fetch_image(camera_url)
    if img is None:
        return jsonify({"status": "error", "message": "Could not fetch image"}), 502
        
    center = detector.detect(img)
    if center is None:
        return jsonify({"status": "not_found", "message": "Nozzle not detected"}), 404
        
    return jsonify({
        "status": "ok",
        "x": center[0],
        "y": center[1]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8085)

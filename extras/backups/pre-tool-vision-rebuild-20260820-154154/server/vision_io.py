# Tool Vision - Camera IO Module
# Based on: kTAMV/server/ktamv_server_io.py
# Handles camera frame capture via HTTP MJPEG stream

import cv2
import numpy as np
import requests
from requests.exceptions import InvalidURL, ConnectionError
import base64

# Frame size - must match server and klippy extension
FRAME_WIDTH = 640
FRAME_HEIGHT = 480


class VisionIO:
    """Handles camera frame I/O: reading MJPEG streams, sending to cloud."""

    def __init__(self, log, camera_url, cloud_url="", save_image=False):
        self.log = log
        self.camera_url = camera_url
        self.cloud_url = cloud_url
        self.save_image = save_image
        self.session = requests.Session()
        self.log("VisionIO: initialized with camera_url=%s" % camera_url)

    def can_read_stream(self, printer):
        """Test if the camera URL is reachable."""
        try:
            with self.session.get(self.camera_url) as _:
                return True
        except InvalidURL:
            raise printer.config_error(
                "Invalid camera URL: %s" % self.camera_url
            )
        except ConnectionError:
            raise printer.config_error(
                "Cannot connect to camera: %s" % self.camera_url
            )
        except Exception as e:
            raise printer.config_error(
                "Camera request failed: %s" % str(e)
            )

    def open_stream(self):
        """Re-open the HTTP session."""
        self.session = requests.Session()

    def get_single_frame(self):
        """Fetch one JPEG frame from the MJPEG stream.

        Reads chunks from the HTTP stream until a complete JPEG is found
        (SOI marker 0xFFD8 to EOI marker 0xFFD9), decodes it with OpenCV,
        and resizes to FRAME_WIDTH x FRAME_HEIGHT.

        Returns:
            numpy.ndarray: BGR image, or None on failure.
        """
        if self.session is None:
            raise Exception("HTTP stream not running")

        try:
            with self.session.get(self.camera_url, stream=True) as stream:
                if stream.ok:
                    chunk_size = 1024
                    bytes_ = b""
                    for chunk in stream.iter_content(chunk_size=chunk_size):
                        bytes_ += chunk
                        # Find JPEG start (SOI) and end (EOI) markers
                        a = bytes_.find(b"\xff\xd8")
                        b = bytes_.find(b"\xff\xd9")
                        if a != -1 and b != -1:
                            jpg = bytes_[a : b + 2]
                            image = cv2.imdecode(
                                np.frombuffer(jpg, dtype=np.uint8),
                                cv2.IMREAD_COLOR,
                            )
                            image = cv2.resize(
                                image,
                                (FRAME_WIDTH, FRAME_HEIGHT),
                                interpolation=cv2.INTER_AREA,
                            )
                            return image
            return None
        except Exception as e:
            self.log("VisionIO: failed to get frame: %s" % str(e))
            return None

    def close_stream(self):
        """Close the HTTP session."""
        if self.session is not None:
            self.session.close()
            self.session = None

    def send_frame_to_cloud(self, frame, points, algorithm):
        """Upload a frame + detection result to the cloud (optional).

        Args:
            frame: OpenCV BGR image
            points: detected nozzle coordinates
            algorithm: which detection combo was used
        """
        if not self.cloud_url:
            return False
        try:
            _, img_encoded = cv2.imencode(".jpg", frame)
            data = {
                "photo": base64.b64encode(img_encoded),
                "algorithm": algorithm,
                "points": str(points),
            }
            response = requests.post(self.cloud_url, data=data)
            if response.status_code != 200:
                self.log(
                    "VisionIO: cloud upload failed (status %d)"
                    % response.status_code
                )
                return False
            return True
        except Exception as e:
            self.log("VisionIO: cloud upload error: %s" % str(e))
            return False

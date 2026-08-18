# Tool Vision - IO Module
# Handles camera frame capture via HTTP stream
# Rebuilt from ktamv_server_io.py

import cv2
import numpy as np
import requests
from requests.exceptions import InvalidURL, ConnectionError
import base64

FRAME_WIDTH = 640
FRAME_HEIGHT = 480


class VisionIO:
    def __init__(self, log, camera_url, cloud_url, save_image=False):
        self.log = log
        self.log(" *** initializing VisionIO **** ")
        self.camera_url = camera_url
        self.save_image = save_image
        self.cloud_url = cloud_url
        self.session = requests.Session()
        self.log(
            " *** VisionIO ready: camera_url=%s **** " % str(camera_url)
        )

    def can_read_stream(self, printer):
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
        self.session = requests.Session()

    def get_single_frame(self):
        if self.session is None:
            raise Exception("HTTP stream not running")

        try:
            with self.session.get(self.camera_url, stream=True) as stream:
                if stream.ok:
                    chunk_size = 1024
                    bytes_ = b""
                    for chunk in stream.iter_content(chunk_size=chunk_size):
                        bytes_ += chunk
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
            self.log("Failed to get frame: %s" % str(e))

    def close_stream(self):
        if self.session is not None:
            self.session.close()
            self.session = None

    def send_frame_to_cloud(self, frame, points, algorithm):
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
                    "Cloud upload failed: status %d" % response.status_code
                )
                return False
            return True
        except Exception as e:
            self.log("Cloud upload error: %s" % str(e))
            return False

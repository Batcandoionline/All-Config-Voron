# Tool Vision - Detection Manager
# Based on: kTAMV/server/ktamv_server_dm.py
# 5-combo nozzle detection with 3 preprocessors + recursive position finding

import copy
import time
import cv2
import numpy as np
from vision_io import VisionIO


class VisionDetectionManager:
    """Manages nozzle detection using OpenCV blob detectors.

    Uses 3 levels of blob detectors (standard, relaxed, super-relaxed)
    combined with 3 image preprocessors to create 5 detection combos.
    Iterates through combos until exactly 1 keypoint is found.
    """

    def __init__(self, log, camera_url, cloud_url="", send_to_cloud=False):
        self.log = log
        self.log("VisionDetectionManager: init")

        self.send_to_cloud = send_to_cloud
        self.io = VisionIO(
            log=log,
            camera_url=camera_url,
            cloud_url=cloud_url,
            save_image=False,
        )
        self.algorithm = None
        self._create_detectors()

        self.log("VisionDetectionManager: ready")

    # ── Detector Setup (3 levels, from kTAMV) ─────────────────

    def _create_detectors(self):
        """Create 3 blob detectors with progressively relaxed parameters.

        Detector params are copied exactly from kTAMV's createDetectors().
        """
        # Standard Parameters - strictest, best for clean nozzles
        self.standard_params = cv2.SimpleBlobDetector_Params()
        self.standard_params.minThreshold = 1
        self.standard_params.maxThreshold = 50
        self.standard_params.thresholdStep = 1
        self.standard_params.filterByArea = True
        self.standard_params.minArea = 400
        self.standard_params.maxArea = 900
        self.standard_params.filterByCircularity = True
        self.standard_params.minCircularity = 0.8
        self.standard_params.maxCircularity = 1
        self.standard_params.filterByConvexity = True
        self.standard_params.minConvexity = 0.3
        self.standard_params.maxConvexity = 1
        self.standard_params.filterByInertia = True
        self.standard_params.minInertiaRatio = 0.3

        # Relaxed Parameters - wider area and circularity range
        self.relaxed_params = cv2.SimpleBlobDetector_Params()
        self.relaxed_params.minThreshold = 1
        self.relaxed_params.maxThreshold = 50
        self.relaxed_params.thresholdStep = 1
        self.relaxed_params.filterByArea = True
        self.relaxed_params.minArea = 600
        self.relaxed_params.maxArea = 15000
        self.relaxed_params.filterByCircularity = True
        self.relaxed_params.minCircularity = 0.6
        self.relaxed_params.maxCircularity = 1
        self.relaxed_params.filterByConvexity = True
        self.relaxed_params.minConvexity = 0.1
        self.relaxed_params.maxConvexity = 1
        self.relaxed_params.filterByInertia = True
        self.relaxed_params.minInertiaRatio = 0.3

        # Super Relaxed Parameters - last resort
        self.super_relaxed_params = cv2.SimpleBlobDetector_Params()
        self.super_relaxed_params.minThreshold = 20
        self.super_relaxed_params.maxThreshold = 200
        self.super_relaxed_params.filterByArea = True
        self.super_relaxed_params.minArea = 200
        self.super_relaxed_params.filterByCircularity = True
        self.super_relaxed_params.minCircularity = 0.5
        self.super_relaxed_params.filterByConvexity = True
        self.super_relaxed_params.minConvexity = 0.5
        self.super_relaxed_params.filterByInertia = True
        self.super_relaxed_params.minInertiaRatio = 0.5
        self.super_relaxed_params.filterByColor = False
        self.super_relaxed_params.minDistBetweenBlobs = 2

        # Create detector instances
        self.detector = cv2.SimpleBlobDetector_create(self.standard_params)
        self.relaxed_detector = cv2.SimpleBlobDetector_create(
            self.relaxed_params
        )
        self.super_relaxed_detector = cv2.SimpleBlobDetector_create(
            self.super_relaxed_params
        )

    # ── Recursive Nozzle Finding (core kTAMV logic) ───────────

    def recursively_find_nozzle_position(
        self, put_frame_func, min_matches, timeout, xy_tolerance
    ):
        """Repeatedly capture frames and detect nozzle until stable position.

        From kTAMV: captures frames, detects nozzle, and requires
        `min_matches` consecutive detections within `xy_tolerance` pixels
        to confirm a stable position.

        Args:
            put_frame_func: callback to display processed frame
            min_matches: consecutive matches required (kTAMV default: 3)
            timeout: seconds before giving up (kTAMV default: 20)
            xy_tolerance: pixel tolerance for match comparison

        Returns:
            tuple (x, y) of nozzle center, or None if not found.
        """
        self.log("recursively_find_nozzle_position: start")
        start_time = time.time()
        last_pos = (0, 0)
        pos_matches = 0
        pos = None

        while time.time() - start_time < timeout:
            frame = self.io.get_single_frame()
            if frame is None:
                continue

            positions, processed_frame = self.nozzle_detection(frame)
            if processed_frame is not None:
                put_frame_func(processed_frame)

            if positions is None or len(positions) == 0:
                continue

            pos = positions

            # Check if position matches previous detection
            if (abs(pos[0] - last_pos[0]) <= xy_tolerance
                    and abs(pos[1] - last_pos[1]) <= xy_tolerance):
                pos_matches += 1
                if pos_matches >= min_matches:
                    self.log(
                        "Found %d consecutive matches, returning." % pos_matches
                    )
                    # Optional cloud upload
                    if self.send_to_cloud:
                        self.io.send_frame_to_cloud(
                            frame, pos, self.algorithm
                        )
                    break
            else:
                self.log(
                    "Position mismatch: last=%s curr=%s diff=X%.3f Y%.3f"
                    % (
                        str(last_pos), str(pos),
                        abs(pos[0] - last_pos[0]),
                        abs(pos[1] - last_pos[1]),
                    )
                )
                pos_matches = 0

            last_pos = pos
            # Wait 0.3s - Crowsnest typically caches ~0.3s of frames
            time.sleep(0.3)

        self.log("Final position: %s" % str(pos))
        return pos

    def get_preview_frame(self, put_frame_func):
        """Capture one frame, run detection, display result."""
        frame = self.io.get_single_frame()
        if frame is None:
            return
        _, processed_frame = self.nozzle_detection(frame)
        if processed_frame is not None:
            put_frame_func(processed_frame)

    # ── 5-Combo Nozzle Detection (core kTAMV logic) ───────────

    def nozzle_detection(self, image):
        """Detect nozzle opening in image using 5 detector+preprocessor combos.

        From kTAMV: tries 5 combinations of detectors and preprocessors
        in order of strictness. Stops at the first combo that finds
        exactly 1 keypoint. If multiple keypoints found, uses the one
        closest to image center (320, 240).

        Combos tried in order:
          1. standard  + preprocessor 0 (YUV adaptive threshold)
          2. standard  + preprocessor 1 (grayscale triangle threshold)
          3. relaxed   + preprocessor 0
          4. relaxed   + preprocessor 1
          5. super-relaxed + preprocessor 2 (median blur)

        Returns:
            (center, processed_frame) where center is (x,y) or None
        """
        work_frame = copy.deepcopy(image)
        keypoints = None

        # Preprocess image with all 3 algorithms
        pp0 = self._preprocess_image(work_frame, algorithm=0)
        pp1 = self._preprocess_image(work_frame, algorithm=1)
        pp2 = self._preprocess_image(work_frame, algorithm=2)

        # Try 5 combos in order of strictness
        # Combo 1: standard detector + preprocessor 0
        keypoints = self.detector.detect(pp0)
        kp_color = (0, 0, 255)  # Red
        if len(keypoints) != 1:
            # Combo 2: standard detector + preprocessor 1
            keypoints = self.detector.detect(pp1)
            kp_color = (0, 255, 0)  # Green
            if len(keypoints) != 1:
                # Combo 3: relaxed detector + preprocessor 0
                keypoints = self.relaxed_detector.detect(pp0)
                kp_color = (255, 0, 0)  # Blue
                if len(keypoints) != 1:
                    # Combo 4: relaxed detector + preprocessor 1
                    keypoints = self.relaxed_detector.detect(pp1)
                    kp_color = (39, 127, 255)  # Orange
                    if len(keypoints) != 1:
                        # Combo 5: super-relaxed + preprocessor 2
                        keypoints = self.super_relaxed_detector.detect(pp2)
                        kp_color = (39, 255, 127)  # Light green
                        if len(keypoints) != 1:
                            keypoints = None
                        else:
                            self.algorithm = 5
                    else:
                        self.algorithm = 4
                else:
                    self.algorithm = 3
            else:
                self.algorithm = 2
        else:
            self.algorithm = 1

        if keypoints is not None:
            self.log(
                "Detected %d circle(s) with combo %s"
                % (len(keypoints), self.algorithm)
            )
        else:
            self.log("Nozzle detection failed (no valid keypoints).")

        # ── Draw detection result on frame ──
        center = None
        if keypoints is not None and len(keypoints) >= 1:
            # If multiple keypoints, pick closest to image center
            if len(keypoints) > 1:
                idx = self._find_closest_keypoint(keypoints)
                (x, y) = np.around(keypoints[idx].pt)
            else:
                (x, y) = np.around(keypoints[0].pt)

            x, y = int(x), int(y)
            center = (x, y)
            radius = int(np.around(keypoints[0].size / 2))

            # Draw filled semi-transparent circle
            circle_frame = cv2.circle(
                img=work_frame, center=center, radius=radius,
                color=kp_color, thickness=-1, lineType=cv2.LINE_AA,
            )
            work_frame = cv2.addWeighted(
                circle_frame, 0.4, work_frame, 0.6, 0
            )
            # Draw circle outline
            work_frame = cv2.circle(
                img=work_frame, center=center, radius=radius,
                color=(0, 0, 0), thickness=1, lineType=cv2.LINE_AA,
            )
            # Draw small crosshair at center
            work_frame = cv2.line(
                work_frame, (x - 5, y), (x + 5, y), (255, 255, 255), 2
            )
            work_frame = cv2.line(
                work_frame, (x, y - 5), (x, y + 5), (255, 255, 255), 2
            )
        else:
            # No detection - draw empty circle at image center
            radius = 17
            work_frame = cv2.circle(
                img=work_frame, center=(320, 240), radius=radius,
                color=(0, 0, 0), thickness=3, lineType=cv2.LINE_AA,
            )
            work_frame = cv2.circle(
                img=work_frame, center=(320, 240), radius=radius + 1,
                color=(0, 0, 255), thickness=1, lineType=cv2.LINE_AA,
            )

        # Draw full-frame crosshair (black bg + white line)
        work_frame = cv2.line(
            work_frame, (320, 0), (320, 480), (0, 0, 0), 2
        )
        work_frame = cv2.line(
            work_frame, (0, 240), (640, 240), (0, 0, 0), 2
        )
        work_frame = cv2.line(
            work_frame, (320, 0), (320, 480), (255, 255, 255), 1
        )
        work_frame = cv2.line(
            work_frame, (0, 240), (640, 240), (255, 255, 255), 1
        )

        return (center, work_frame)

    # ── Image Preprocessors (from kTAMV) ──────────────────────

    def _preprocess_image(self, frame_input, algorithm=0):
        """Apply image preprocessing for nozzle detection.

        From kTAMV: 3 preprocessing algorithms:
          0: YUV color space → Gaussian blur → adaptive threshold
          1: Grayscale → triangle threshold → Gaussian blur
          2: Grayscale → median blur

        All start with gamma correction (gamma=1.2).
        """
        try:
            output = self._adjust_gamma(image=frame_input, gamma=1.2)
        except:
            output = copy.deepcopy(frame_input)

        if algorithm == 0:
            yuv = cv2.cvtColor(output, cv2.COLOR_BGR2YUV)
            planes = cv2.split(yuv)
            plane0 = cv2.GaussianBlur(planes[0], (7, 7), 6)
            plane0 = cv2.adaptiveThreshold(
                plane0, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                35, 1,
            )
            output = cv2.cvtColor(plane0, cv2.COLOR_GRAY2BGR)

        elif algorithm == 1:
            output = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
            _, output = cv2.threshold(
                output, 127, 255,
                cv2.THRESH_BINARY | cv2.THRESH_TRIANGLE,
            )
            output = cv2.GaussianBlur(output, (7, 7), 6)
            output = cv2.cvtColor(output, cv2.COLOR_GRAY2BGR)

        elif algorithm == 2:
            gray = cv2.cvtColor(frame_input, cv2.COLOR_BGR2GRAY)
            output = cv2.medianBlur(gray, 5)

        return output

    def _find_closest_keypoint(self, keypoints):
        """Find the keypoint closest to image center (320, 240)."""
        closest_index = None
        closest_distance = float("inf")
        target = np.array([320, 240])

        for i, kp in enumerate(keypoints):
            point = np.array(kp.pt)
            distance = np.linalg.norm(point - target)
            if distance < closest_distance:
                closest_distance = distance
                closest_index = i

        return closest_index

    def _adjust_gamma(self, image, gamma=1.2):
        """Apply gamma correction to brighten/darken image."""
        inv_gamma = 1.0 / gamma
        table = np.array(
            [((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]
        ).astype("uint8")
        return cv2.LUT(image, table)

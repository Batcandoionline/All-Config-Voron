import copy
import cv2
import numpy as np
import logging

class VisionDetector:
    def __init__(self, log_func=print):
        self.log = log_func
        self.algorithm = None
        self.createDetectors()

    def createDetectors(self):
        # Standard Parameters
        self.standardParams = cv2.SimpleBlobDetector_Params()
        self.standardParams.minThreshold = 1
        self.standardParams.maxThreshold = 50
        self.standardParams.thresholdStep = 1
        self.standardParams.filterByArea = True
        self.standardParams.minArea = 400
        self.standardParams.maxArea = 900
        self.standardParams.filterByCircularity = True
        self.standardParams.minCircularity = 0.8
        self.standardParams.maxCircularity = 1
        self.standardParams.filterByConvexity = True
        self.standardParams.minConvexity = 0.3
        self.standardParams.maxConvexity = 1
        self.standardParams.filterByInertia = True
        self.standardParams.minInertiaRatio = 0.3

        # Relaxed Parameters
        self.relaxedParams = cv2.SimpleBlobDetector_Params()
        self.relaxedParams.minThreshold = 1
        self.relaxedParams.maxThreshold = 50
        self.relaxedParams.thresholdStep = 1
        self.relaxedParams.filterByArea = True
        self.relaxedParams.minArea = 600
        self.relaxedParams.maxArea = 15000
        self.relaxedParams.filterByCircularity = True
        self.relaxedParams.minCircularity = 0.6
        self.relaxedParams.maxCircularity = 1
        self.relaxedParams.filterByConvexity = True
        self.relaxedParams.minConvexity = 0.1
        self.relaxedParams.maxConvexity = 1
        self.relaxedParams.filterByInertia = True
        self.relaxedParams.minInertiaRatio = 0.3

        # Super Relaxed Parameters
        self.superRelaxedParams = cv2.SimpleBlobDetector_Params()
        self.superRelaxedParams.minThreshold = 20
        self.superRelaxedParams.maxThreshold = 200
        self.superRelaxedParams.filterByArea = True
        self.superRelaxedParams.minArea = 200
        self.superRelaxedParams.filterByCircularity = True
        self.superRelaxedParams.minCircularity = 0.5
        self.superRelaxedParams.filterByConvexity = True
        self.superRelaxedParams.minConvexity = 0.5
        self.superRelaxedParams.filterByInertia = True
        self.superRelaxedParams.minInertiaRatio = 0.5
        self.superRelaxedParams.filterByColor = False
        self.superRelaxedParams.minDistBetweenBlobs = 2

        self.detector = cv2.SimpleBlobDetector_create(self.standardParams)
        self.relaxedDetector = cv2.SimpleBlobDetector_create(self.relaxedParams)
        self.superRelaxedDetector = cv2.SimpleBlobDetector_create(self.superRelaxedParams)

    def nozzleDetection(self, image):
        nozzleDetectFrame = copy.deepcopy(image)
        keypoints = None
        center = (None, None)

        preprocessorImage0 = self.preprocessImage(frameInput=nozzleDetectFrame, algorithm=0)
        preprocessorImage1 = self.preprocessImage(frameInput=nozzleDetectFrame, algorithm=1)
        preprocessorImage2 = self.preprocessImage(frameInput=nozzleDetectFrame, algorithm=2)

        # Apply combo 1
        keypoints = self.detector.detect(preprocessorImage0)
        keypointColor = (0,0,255)
        if len(keypoints) != 1:
            # combo 2
            keypoints = self.detector.detect(preprocessorImage1)
            keypointColor = (0,255,0)
            if len(keypoints) != 1:
                # combo 3
                keypoints = self.relaxedDetector.detect(preprocessorImage0)
                keypointColor = (255,0,0)
                if len(keypoints) != 1:
                    # combo 4
                    keypoints = self.relaxedDetector.detect(preprocessorImage1)
                    keypointColor = (39,127,255)
                    if len(keypoints) != 1:
                        # combo 5
                        keypoints = self.superRelaxedDetector.detect(preprocessorImage2)
                        keypointColor = (39,255,127)
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

        if keypoints is not None and len(keypoints) >= 1:
            if len(keypoints) > 1:
                closest_index = self.find_closest_keypoint(keypoints)
                (x,y) = np.around([keypoints[closest_index].pt])[0]
            else:
                (x,y) = np.around(keypoints[0].pt)
                
            x,y = int(x), int(y)
            center = (x,y)
            keypointRadius = int(np.around(keypoints[0].size/2))
            circleFrame = cv2.circle(img=nozzleDetectFrame, center=center, radius=keypointRadius,color=keypointColor,thickness=-1,lineType=cv2.LINE_AA)
            nozzleDetectFrame = cv2.addWeighted(circleFrame, 0.4, nozzleDetectFrame, 0.6, 0)
            nozzleDetectFrame = cv2.circle(img=nozzleDetectFrame, center=center, radius=keypointRadius, color=(0,0,0), thickness=1,lineType=cv2.LINE_AA)
            nozzleDetectFrame = cv2.line(nozzleDetectFrame, (x-5,y), (x+5, y), (255,255,255), 2)
            nozzleDetectFrame = cv2.line(nozzleDetectFrame, (x,y-5), (x, y+5), (255,255,255), 2)
        else:
            keypointRadius = 17
            nozzleDetectFrame = cv2.circle(img=nozzleDetectFrame, center=(320,240), radius=keypointRadius, color=(0,0,0), thickness=3,lineType=cv2.LINE_AA)
            nozzleDetectFrame = cv2.circle(img=nozzleDetectFrame, center=(320,240), radius=keypointRadius+1, color=(0,0,255), thickness=1,lineType=cv2.LINE_AA)
            center = None
            
        # Draw crosshair
        nozzleDetectFrame = cv2.line(nozzleDetectFrame, (320,0), (320,480), (0,0,0), 2)
        nozzleDetectFrame = cv2.line(nozzleDetectFrame, (0,240), (640,240), (0,0,0), 2)
        nozzleDetectFrame = cv2.line(nozzleDetectFrame, (320,0), (320,480), (255,255,255), 1)
        nozzleDetectFrame = cv2.line(nozzleDetectFrame, (0,240), (640,240), (255,255,255), 1)

        return (center, nozzleDetectFrame)

    def preprocessImage(self, frameInput, algorithm=0):
        try:
            outputFrame = self.adjust_gamma(image=frameInput, gamma=1.2)
        except:
            outputFrame = copy.deepcopy(frameInput)
            
        if algorithm == 0:
            yuv = cv2.cvtColor(outputFrame, cv2.COLOR_BGR2YUV)
            yuvPlanes = cv2.split(yuv)
            yuvPlanes_0 = cv2.GaussianBlur(yuvPlanes[0],(7,7),6)
            yuvPlanes_0 = cv2.adaptiveThreshold(yuvPlanes_0,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,35,1)
            outputFrame = cv2.cvtColor(yuvPlanes_0,cv2.COLOR_GRAY2BGR)
        elif algorithm == 1:
            outputFrame = cv2.cvtColor(outputFrame, cv2.COLOR_BGR2GRAY )
            thr_val, outputFrame = cv2.threshold(outputFrame, 127, 255, cv2.THRESH_BINARY|cv2.THRESH_TRIANGLE )
            outputFrame = cv2.GaussianBlur( outputFrame, (7,7), 6 )
            outputFrame = cv2.cvtColor( outputFrame, cv2.COLOR_GRAY2BGR )
        elif algorithm == 2:
            gray = cv2.cvtColor(frameInput, cv2.COLOR_BGR2GRAY)
            outputFrame = cv2.medianBlur(gray, 5)

        return outputFrame

    def find_closest_keypoint(self, keypoints):
        closest_index = None
        closest_distance = float('inf')
        target_point = np.array([320, 240])

        for i, keypoint in enumerate(keypoints):
            point = np.array(keypoint.pt)
            distance = np.linalg.norm(point - target_point)

            if distance < closest_distance:
                closest_distance = distance
                closest_index = i
        return closest_index

    def adjust_gamma(self, image, gamma=1.2):
        invGamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype('uint8')
        return cv2.LUT(image, table)

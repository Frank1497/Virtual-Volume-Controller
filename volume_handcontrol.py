import cv2 as cv
import time

import numpy as np

import hand_tracking_module as htm
import numpy
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


cap = cv.VideoCapture(0)
pTime = 0
detector = htm.handDetector(min_detection_confidence=0.7, min_tracking_confidence=0.7)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
#volume.SetMasterVolumeLevel(-7, None)
print(volRange)
maxvol = volRange[1]
minvol = volRange[0]

vol = 0
volBar = 400
volPer = 0
# wCam, hCam = 1280, 720
# cap.set(3, wCam)
# cap.set(4, hCam)
while True:
    suc, vid = cap.read()
    vid = detector.findHands(vid)
    lmlist = detector.findPosition(vid)
    if len(lmlist) !=0:
        # print(lmlist[4], lmlist[8])
        x1, y1 = lmlist[4][1], lmlist[4][2]
        x2, y2 = lmlist[8][1], lmlist[8][2]
        cx, cy = ((x1 + x2)//2), ((y1 + y2)//2)

        cv.circle(vid, (x1, y1), 10, (255, 0, 255), cv.FILLED)
        cv.circle(vid, (x2, y2), 10, (255, 0, 255), cv.FILLED)
        cv.circle(vid, (cx, cy), 7, (255, 0, 255), cv.FILLED)
        cv.line(vid, (x1, y1), (x2, y2), (255, 0, 255), 3)


        length = math.hypot(x2-x1, y2-y1)
        # print(length)

        # hand range 35-200
        # volume range 0.0 - -76
        vol = np.interp(length, [30, 180], [minvol, maxvol])
        volBar = np.interp(length, [30, 180], [400, 150])
        volPer = np.interp(length, [30, 180], [0, 100])
        #print(vol, int(length))
        volume.SetMasterVolumeLevel(vol, None)

        if length < 30:
            cv.circle(vid, (cx, cy), 7, (0, 255, 0), cv.FILLED)

    cv.rectangle(vid, (50, 150), (85, 400), (0, 255, 0), 3)
    cv.rectangle(vid, (50, int(volBar)), (85, 400), (0, 255, 0), cv.FILLED)
    cv.putText(vid, f'{int(volPer)}', (40, 450), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)


    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv.putText(vid, f'FPS: {int(fps)}', (40, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 69), 2)
    cv.imshow('VIDEO', vid)
    if cv.waitKey(1) & 0xFF == ord("q"):
        break
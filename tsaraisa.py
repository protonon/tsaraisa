#!/usr/bin/env python

# Copyright 2014 Jarmo Puttonen <jarmo.puttonen@gmail.com>. All rights reserved.
# Use of this source code is governed by a MIT-style
# licence that can be found in the LICENCE file.

"""Detect speed limits from webcam feed"""
import re
import os
import sys
import cv2
import threading
import argparse
from gps import gps, WATCH_ENABLE

def onTrackbarChange(_):
    """Pass any trackbar changes"""

class GPSInfo(threading.Thread):
    """Thread that takes care of updating GPS Speed info."""
    def __init__(self):
        threading.Thread.__init__(self)
        self.gpsd = gps(mode=WATCH_ENABLE)
        self.running = True
        self.speed = 0

    def run(self):
        while self.running:
            self.gpsd.next()
            self.speed = self.gpsd.fix.speed*3.6 #from m/s to km/h

def read_paths(path):
    """Returns a list of files in given path"""
    images = [[] for _ in range(2)]
    for dirname, dirnames, _ in os.walk(path):
        for subdirname in dirnames:
            filepath = os.path.join(dirname, subdirname)
            for filename in os.listdir(filepath):
                try:
                    imgpath = str(os.path.join(filepath, filename))
                    images[0].append(imgpath)
                    limit = re.findall('[0-9]+', filename)
                    images[1].append(limit[0])
                except IOError, (errno, strerror):
                    print "I/O error({0}): {1}".format(errno, strerror)
                except:
                    print "Unexpected error:", sys.exc_info()[0]
                    raise
    return images

def load_images(imgpath):
    """Loads images in given path and returns
     a list containing image and keypoints"""
    images = read_paths(imgpath)
    imglist = [[], [], [], []]
    cur_img = 0
    sift = cv2.SIFT()
    for i in images[0]:
        img = cv2.imread(i, 0)
        imglist[0].append(img)
        imglist[1].append(images[1][cur_img])
        cur_img += 1
        keypoints, des = sift.detectAndCompute(img, None)
        imglist[2].append(keypoints)
        imglist[3].append(des)
    return imglist

def run_flann(img):
    """Run FLANN-detector for given image with given image list"""
# Find the keypoint descriptors with SIFT
    _, des = SIFT.detectAndCompute(img, None)
    if des is None:
        return "Unknown", 0
    if len(des) < ARGS.MINKP:
        return "Unknown", 0

    biggest_amnt = 0
    biggest_speed = 0
    cur_img = 0
    try:
        for _ in IMAGES[0]:
            des2 = IMAGES[3][cur_img]
            matches = FLANN.knnMatch(des2, des, k=2)
            matchamnt = 0
    # Find matches with Lowe's ratio test
            for _, (moo, noo) in enumerate(matches):
                if moo.distance < ARGS.FLANNTHRESHOLD*noo.distance:
                    matchamnt += 1
            if matchamnt > biggest_amnt:
                biggest_amnt = matchamnt
                biggest_speed = IMAGES[1][cur_img]
            cur_img += 1
        if biggest_amnt > ARGS.MINKP:
            return biggest_speed, biggest_amnt
        else:
            return "Unknown", 0
    except Exception, exept:
        print exept
        return "Unknown", 0

IMAGES = load_images("data")

def run_logic():
    """Run TSR and ISA"""
    lastlimit = "00"
    lastdetect = "00"
    downscale = ARGS.DOWNSCALE
    matches = 0
    possiblematch = "00"
    try:
        if CAP.isOpened():
            rval, frame = CAP.read()
            print("Camera opened and frame read")
        else:
            rval = False
            print("Camera not opened")
        while rval:
            origframe = frame
            if ARGS.MORPH:
                frame = cv2.morphologyEx(
                    frame,
                    cv2.MORPH_OPEN, 
                    cv2.getStructuringElement(cv2.MORPH_RECT,(2,2))
                    )
                frame = cv2.morphologyEx(
                    frame, 
                    cv2.MORPH_CLOSE, 
                    cv2.getStructuringElement(cv2.MORPH_RECT,(2,2))
                    )
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if ARGS.EQ:
                cv2.equalizeHist(frame, frame)
            if ARGS.TRACKBARS:
                ARGS.MINKP = cv2.getTrackbarPos('MINKEYPOINTS','preview')
                downscale = cv2.getTrackbarPos('DOWNSCALE','preview')
                ARGS.FLANNTHRESHOLD = float(
                    cv2.getTrackbarPos('FLANNTHRESHOLD','preview')
                    )/10
                ARGS.CHECKS = cv2.getTrackbarPos('FLANNCHECKS','preview')
                ARGS.TREES = cv2.getTrackbarPos('FLANNTREES','preview')

            scaledsize = (frame.shape[1]/downscale, frame.shape[0]/downscale)
            scaledframe = cv2.resize(frame, scaledsize)

            # Detect signs in downscaled frame
            signs = CLASSIFIER.detectMultiScale(
                scaledframe,
                1.1,
                5,
                0,
                (10, 10),
                (200, 200))
            for sign in signs:
                xpos, ypos, width, height = [ i*downscale for i in sign ]

                crop_img = frame[ypos:ypos+height, xpos:xpos+width]
                sized = cv2.resize(crop_img, (128, 128))
                comp = "Unknown"
                comp, amnt  = run_flann(sized)
                if comp != "Unknown":
                    if comp != lastlimit:
                        # Require two consecutive hits for new limit.
                        if comp == lastdetect:
                            possiblematch = comp
                            matches = matches + 1
                            if matches >= ARGS.matches:
                                print "New speed limit: "+possiblematch
                                lastlimit = possiblematch
                                matches = 0
                        else:
                            possiblematch = "00"
                            matches = 0
                    cv2.rectangle(
                        origframe, 
                        (xpos, ypos), 
                        (xpos+width, ypos+height), 
                        (0, 0, 255))
                    cv2.putText(
                        origframe,
                        "Speed limit: "+comp+" KP: "+str(amnt),
                        (xpos,ypos-5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                         0.4,
                        (0,0,255),
                        1,)
                else:
                    cv2.rectangle(
                        origframe,
                        (xpos,ypos),
                        (xpos+width,ypos+height),
                        (255,0,0))
                    cv2.putText(
                        origframe,
                        "UNKNOWN SPEED LIMIT",
                        (xpos,ypos-5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,
                        (255,0,0),
                        1,)
                    comp = lastdetect
                lastdetect = comp

            cv2.putText(
            origframe,
            "Current speed limit: "+str(lastlimit)+" km/h.",
            (5,50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,0,0),
            2
            )

            if ARGS.GPS:
                curspeed = GPSP.speed
                #debug value used when testing on non-moving environment.
                #curspeed = GPSP.speed*200 
                if lastlimit != "00":
                    overspeed = curspeed - float(lastdetect)
                else:
                    overspeed = 0
                if overspeed <= 0:
                    cv2.putText(
                        origframe,
                        "Current speed: "+str(curspeed)+" km/h.",
                        (5,100),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0,0,0),
                        2)

                if overspeed > 0:
                    print("OVERSPEED ",
                        curspeed+overspeed, 
                        " km/h!", 
                        overspeed, 
                        " km/h over speedlimit."
                        )
                    cv2.putText(
                        origframe,
                        "Overspeed "+str(curspeed+overspeed)+" km/h!",
                        (5,100),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0,0,255),
                        2)

            if ARGS.PREVIEW:
                cv2.imshow("preview", origframe)

            _ = cv2.waitKey(20)
            rval, frame = CAP.read()
    except (KeyboardInterrupt, Exception), exept:
        print exept
        if ARGS.GPS:
            print "Killing GPS"
            GPSP.running = False
            GPSP.join()
        print "Shutting down!"

# Preload all classes used in detection
SIFT = cv2.SIFT()
INDEX_PARAMS = None
SEARCH_PARAMS = None
FLANN = None
## Webcam logic starts
CAP = None
ARGS = None

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(
      description="Traffic sign recognition and intelligent speed assist.",
      )

    PARSER.add_argument("-d", "--device", dest="SOURCE", default=0,
      help="Index of used video device. Default: 0 (/dev/video0).")
    PARSER.add_argument("-g", "--gps", 
        dest="GPS", action="store_true", default=False,
      help="Enable over speeding detection.")
    PARSER.add_argument("-o", "--overspeed", 
        dest="COMMAND", default="false",
      help="Command used in overspeed warning." \
      " Default: echo OVERSPEEDING!.")
    PARSER.add_argument("-c", "--cascade", 
        dest="CASCADE", default="lbpCascade.xml",
      help="Cascade used in speed sign detection." \
      " Default: lbpCascade.xml.")
    PARSER.add_argument("-k", "--keypoints", 
        dest="MINKP", default=5,
      help="Min amount of keypoints required in" \
      " limit recognition. Default: 5.")
    PARSER.add_argument("-D", "--downscale", 
        dest="DOWNSCALE", default=1,
      help="Multiplier for downscaling frame before" \
      " detecting signs. Default: 1.")
    PARSER.add_argument("-f", "--flann", 
        dest="FLANNTHRESHOLD", default=0.8,
      help="Threshold multiplier for accepting FLANN matches." \
      " Default: 0.8.")
    PARSER.add_argument("-F", "--flannchecks", 
        dest="CHECKS", default=50,
      help="How many checks will be done in FLANN matching." \
      " Default: 50.")
    PARSER.add_argument("-t", "--flanntrees", 
        dest="TREES", default=5,
      help="How many trees will be used in FLANN matching." \
      " Default: 5.")
    PARSER.add_argument("-m", "--matches", 
        dest="matches", default=2,
      help="How many consecutive keypoint matches are needed" \
      " before setting new limit. Default: 2.")
    PARSER.add_argument("-e", "--disable-eq", 
        dest="EQ", action="store_false", default=True,
      help="Disable histogram equalization.")
    PARSER.add_argument("-M", "--morphopenclose", 
        dest="MORPH", action="store_true", default=False,
      help="Enable morphological open/close used in removing" \
      " noise from image.")
    PARSER.add_argument("-T", "--trackbars", 
        dest="TRACKBARS", action="store_true", default=False,
      help="Enable debug trackbars.")
    PARSER.add_argument("-s", "--showvid", 
        dest="PREVIEW", action="store_true", default=False,
      help="Show output video with detections.")
    ARGS = PARSER.parse_args()

    CAP = cv2.VideoCapture(int(ARGS.SOURCE))
    CLASSIFIER = cv2.CascadeClassifier(ARGS.CASCADE)
    INDEX_PARAMS = dict(algorithm = 0, trees = ARGS.TREES)
    SEARCH_PARAMS = dict(checks=ARGS.CHECKS)   # or pass empty dictionary

    FLANN = cv2.FlannBasedMatcher(INDEX_PARAMS, SEARCH_PARAMS)

    if ARGS.PREVIEW:
        cv2.namedWindow("preview")

    if ARGS.GPS:
        GPSP = GPSInfo()
        GPSP.start()

    if ARGS.TRACKBARS:
        cv2.createTrackbar(
            'MINKEYPOINTS', 
            'preview', 
            ARGS.MINKP, 
            100, 
            onTrackbarChange)
        cv2.createTrackbar(
            'DOWNSCALE', 
            'preview', 
            int(ARGS.DOWNSCALE),
            20,
            onTrackbarChange)
        cv2.createTrackbar(
            'FLANNTHRESHOLD',
            'preview',
            8,
            10,
            onTrackbarChange)
        cv2.createTrackbar(
            'FLANNCHECKS', 
            'preview', 
            ARGS.CHECKS, 
            1000, 
            onTrackbarChange)
        cv2.createTrackbar(
            'FLANNTREES', 
            'preview', 
            ARGS.TREES, 
            50, 
            onTrackbarChange)
    run_logic()

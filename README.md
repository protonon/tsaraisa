Tsaraisa
-

_Traffic sign automatic recognition and intelligent speed assist._

[![endorse](http://api.coderwall.com/putsi/endorsecount.png)](http://coderwall.com/putsi)
![Demo screenshot](https://github.com/putsi/tsaraisa/raw/master/tsaraisa.png "Driving on icy Finnish road")
Tsaraisa was run with "./tsaraisa.py -s -g -c lbpCascade.xml -M" on demo screenshot.

What does it do?
-
* Detect traffic signs.
* Recognize speed limits in signs.
* (optional) Compare GPS-speed to speed limit.
* (optional) Run user command when overspeeding.

How?
-
**GPS-class**
* Uses threading to update GPS-info automatically.
* Gets speed from GPS-daemon using python bindings.

**Frame handling**
* Reads frame from webcam.
* Converts frame to grayscale with cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).
* (optional) Morphological Open/close.
* (optional) Equalizes histograms with cv2.equalizeHist().
* Downscale frame with multiplier n.

**Traffic sign detection**
* Uses LBP- or HAAR-cascade to detect speed signs.
* LBP-cascade was trained with 2000 positive and 1000 negative images.
  * Negative image is image of road without speed limit sign.
  * Positive image is image of road with speed limit sign.
* LBP- and HAAR-detection allows great differences in lightning.
* LBP- and HAAR-detection works great on low performance machines.

**Recognizing speed limits**
* Uses Fast Approximate Nearest Neighbor Search Library feature matching.
* Creates "keypoints" of detected sign and compares them to all known speed limits (files in data-folder).
* Keypoint match distances need to be inside a threshold.
* Match with biggest proper keypoint amount will be returned.
* It is fast and pretty accurate with different lightning conditions.

**Speed assist**
* When new speed limit is detected it is added as current speed limit.
* After every frame script compares current speed to current speed limit.
* Script runs specified command when overspeeding (e.g. "beep").

Requirements
-
**Required software**
* OpenCV >=3.0.0
* Python >=2.7.3
* LibAV >=0.8.10
* (optional) gpsd && python-gps
* (optional) V4L2 1.0.1

**Required hardware**
* Webcam or some other video-source.
* (optional) GPS Module BU-353

Usage
-
```
usage: tsaraisa.py [-h] [-d SOURCE] [-g] [-o COMMAND] [-c CASCADE] [-k MINKP]
                 [-D DOWNSCALE] [-f FLANNTHRESHOLD] [-F CHECKS] [-t TREES]
                 [-m MATCHES] [-e] [-M] [-T] [-s]

Traffic sign recognition and intelligent speed assist.

optional arguments:
  -h, --help            show this help message and exit
  -d SOURCE, --device SOURCE
                        Index of used video device. Default: 0 (/dev/video0).
  -g, --gps             Enable over speeding detection.
  -o COMMAND, --overspeed COMMAND
                        Command used in overspeed warning. Default: echo
                        OVERSPEEDING!.
  -c CASCADE, --cascade CASCADE
                        Cascade used in speed sign detection. Default:
                        lbpCascade.xml.
  -k MINKP, --keypoints MINKP
                        Min amount of keypoints required in limit recognition.
                        Default: 5.
  -D DOWNSCALE, --downscale DOWNSCALE
                        Multiplier for downscaling frame before detecting
                        signs. Default: 1.
  -f FLANNTHRESHOLD, --flann FLANNTHRESHOLD
                        Threshold multiplier for accepting FLANN matches.
                        Default: 0.8.
  -F CHECKS, --flannchecks CHECKS
                        How many checks will be done in FLANN matching.
                        Default: 50.
  -t TREES, --flanntrees TREES
                        How many trees will be used in FLANN matching.
                        Default: 5.
  -m MATCHES, --matches MATCHES
                        How many consecutive keypoint matches are needed
                        before setting new limit. Default: 2.
  -e, --disable-eq      Disable histogram equalization.
  -M, --morphopenclose  Enable morphological open/close used in removing noise
                        from image.
  -T, --trackbars       Enable debug trackbars.
  -s, --showvid         Show output video with detections.
```

Accuracy and performance
-
* Very low false positives with LBP- and HAAR-cascades.
* Plenty of false positives with FLANN-recognition.

How to improve?
-
**Better cascade**
* Get proper negative images (atleast 2000).
* Get proper positive images (atleast 2000).
* Positives and negatives on every weather condition.
* Multiple versions from every sign image.
  * Dirty, broken, old, partial, overexposured...
* NOTE: Training LBP-cascade requires usually hours, HAAR-cascade days.
* NOTE: To create a cascade that detects all speed limits, remove speed limit numbers from positive images (I just left the middle of sign transparent).

**Better keypoint samples**
* Use better algorithm.
* Get CAD-pictures of speed limits from Finnish Transport Agency.

**Optimizations**
* Convert to C++ (1-10% increase in performance).
* Use hardware that supports [CUDA](http://opencv.org/platforms/cuda.html), [TBB](https://www.threadingbuildingblocks.org/), and/or [NEON](http://www.arm.com/products/processors/technologies/neon.php) acceleration (Compile OpenCV with selected acceleration method enabled.).

**Known problems**
* Different webcams require finding correct command line arguments.
* When using low resolutions, sign detection range is very low.
* Cascades were trained fastly so not as good as could be.

Licence
-
See LICENCE file.

Copyright 2014 Jarmo Puttonen <jarmo.puttonen@gmail.com>.

#!/usr/bin/python

import jetson.inference
import jetson.utils
import serial
from time import sleep

import argparse, sys, time, random
from label import *

from chad_helper import *


HEIGHT = 720
WIDTH = 1280
GLOBAL_MOTOR_MAX_SPEED = 30
W_MIDPOINT = int(WIDTH/2)
H_MIDPOINT = int(HEIGHT/2)

# parse the command line
parser = argparse.ArgumentParser(description="Locate objects in a live camera stream using an object detection DNN.", 
                           formatter_class=argparse.RawTextHelpFormatter, epilog=jetson.inference.detectNet.Usage())

parser.add_argument("--network", type=str, default="ssd-mobilenet-v2", help="pre-trained model to load (see below for options)")
parser.add_argument("--overlay", type=str, default="box,labels,conf", help="detection overlay flags (e.g. --overlay=box,labels,conf)\nvalid combinations are:  'box', 'labels', 'conf', 'none'")
parser.add_argument("--threshold", type=float, default=0.3, help="minimum detection threshold to use") 
parser.add_argument("--camera", type=str, default="/dev/video1", help="index of the MIPI CSI camera to use (e.g. CSI camera 0)\nor for VL42 cameras, the /dev/video device to use.\nby default, MIPI CSI camera 0 will be used.")
parser.add_argument("--width", type=int, default=WIDTH, help="desired width of camera stream (default is 1280 pixels)")
parser.add_argument("--height", type=int, default=HEIGHT, help="desired height of camera stream (default is 720 pixels)")

parser.add_argument('--debug', dest='DEBUG', action='store_true')
parser.add_argument('--no-debug', dest='DEBUG', action='store_false')
parser.set_defaults(DEBUG=True)


try:
    opt = parser.parse_known_args()[0]
    DEBUG = opt.DEBUG 
    cam = int(opt.camera[-1])
except:
    print("")
    parser.print_help()
    sys.exit(0)

####### ZED Camera Config
import cv2
import numpy as np

# Open the ZED camera
cap = cv2.VideoCapture(cam)
if cap.isOpened() == 0:
    exit(-1)

# Set the video resolution to HD720 (2560*720)

# Different Resolutions: (WIDTH, HEIGHT)
# 1. HD720: 2560,720
# 2. HD1080: 3840, 1080

R_WIDTH = 3840
R_HEIGHT = 1080

cap.set(cv2.CAP_PROP_FRAME_WIDTH, R_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, R_HEIGHT)

#######

# load the object detection network
# raise Exception(sys.argv)
net = jetson.inference.detectNet(opt.network, sys.argv, opt.threshold)
# cam = Camera(0)

# create the camera and display
camera = jetson.utils.gstCamera(opt.width, opt.height, opt.camera)
display = jetson.utils.glDisplay()

INTERESTS = [44, 47, 48, 49, 50]
SAMPLE = [62, 72, 8, 33]

def lower_half(img):
    y = img.shape[0]
    x = img.shape[1]
    new_img = img[int(y/2):int(15*y/20),0:x]
    return new_img, new_img.shape[1], new_img.shape[0]

if not DEBUG:
    ser = serial.Serial('/dev/ttyACM0')

nav = Navigator(serial=ser)

try:
    while True:
        #### capture the image
        retval, frame = cap.read()
        # Extract left and right images from side-by-side
        left_right_image = np.split(frame, 2, axis=1)
        left = cv2.rotate(left_right_image[0], cv2.ROTATE_90_CLOCKWISE)
        right = cv2.rotate(left_right_image[1], cv2.ROTATE_90_CLOCKWISE)

        input_image, x, y = lower_half(left)

        input_image = cv2.cvtColor(input_image, cv2.COLOR_RGB2RGBA).astype(np.float32)
        input_image = jetson.utils.cudaFromNumpy(input_image)
        # detect objects in the image (with overlay)
        detections = net.Detect(input_image, x, y, opt.overlay)
        found = False
        if DEBUG and display.IsOpen():
            display.RenderOnce(input_image, x, y)

        for detection in detections:
            # 1. Is it an object we want to get?
            # 2. Where is the object relative to the screen?
            # 3. How close to the robot (ping sensor)
            if found is False and detection.ClassID in INTERESTS and detection.Confidence > .50:
                if DEBUG:
                    # print(detection.ClassID, align_to_center_horizontal(detection.Center), ask_distance())
                    sleep(.1)
                    w, h = detection.Center
                    print(detection.Center)
                    if h < H_MIDPOINT:
                        print("Near the center ", h, detection.Center)
                else:

                    w_local, h_local = detection.Center
                    nav.update_target(w_local, h_local)

                    # This portion assumes that the target object is centered by the width of the frame.
                    # Now we control to move forwards or backwards then pick up the object 
                    if (W_MIDPOINT-40) < w_local < (W_MIDPOINT+40):
                        # TODO: Need to work on forward/backward movements.
                        # Stop whatever commands was sent before.
                        left_right_image = np.split(frame, 2, axis=1)
                        right = cv2.rotate(left_right_image[1], cv2.ROTATE_90_CLOCKWISE)

                        input_image, x, y = lower_half(left)

                        input_image = cv2.cvtColor(input_image, cv2.COLOR_RGB2RGBA).astype(np.float32)
                        input_image = jetson.utils.cudaFromNumpy(input_image)
                        lower_detections = net.Detect(input_image, x, y, opt.overlay)

                        for i in lower_detections:
                            if detection.ClassID == i:
                                w_, h_ = i.Center
                                nav.update_target(w_, h_)
                                nav.forward()

                            if (H_MIDPOINT-20) < h_local < (H_MIDPOINT+20):
                                
                                ser.write(b'stop')
                                scoop = run_scoop()
                                if scoop is not None:
                                    running = ser.write(scoop)
                                    
                                    # We need to block controls until it returns the response scooped.
                                    while running is not 'scooped':
                                        sleep(0.01)
                            else:
                                ser.write(align_to_center_vertical(detection.Center))

                    # This portion of the code assumes the object is the side of the frame, so we try to 
                    # align as close to the midpoint of the width of the frame
                    else:
                        ser.write(align_to_center_horizontal(detection.Center))
                found = True
            else:
                nav.blind_run()

except:
    if not DEBUG:
        ser.write(b'stop')
        ser.close()
    raise

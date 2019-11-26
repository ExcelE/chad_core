#!/usr/bin/python
#
# Copyright (c) 2019, NVIDIA CORPORATION. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

import jetson.inference
import jetson.utils
import serial
# from pseyepy import Camera

import argparse, sys, time, random
from label import *

HEIGHT = 720
WIDTH = 1280

# parse the command line
parser = argparse.ArgumentParser(description="Locate objects in a live camera stream using an object detection DNN.", 
						   formatter_class=argparse.RawTextHelpFormatter, epilog=jetson.inference.detectNet.Usage())

parser.add_argument("--network", type=str, default="ssd-mobilenet-v2", help="pre-trained model to load (see below for options)")
parser.add_argument("--overlay", type=str, default="box,labels,conf", help="detection overlay flags (e.g. --overlay=box,labels,conf)\nvalid combinations are:  'box', 'labels', 'conf', 'none'")
parser.add_argument("--threshold", type=float, default=0.5, help="minimum detection threshold to use") 
parser.add_argument("--camera", type=str, default="0", help="index of the MIPI CSI camera to use (e.g. CSI camera 0)\nor for VL42 cameras, the /dev/video device to use.\nby default, MIPI CSI camera 0 will be used.")
parser.add_argument("--width", type=int, default=WIDTH, help="desired width of camera stream (default is 1280 pixels)")
parser.add_argument("--height", type=int, default=HEIGHT, help="desired height of camera stream (default is 720 pixels)")

try:
	opt = parser.parse_known_args()[0]
except:
	print("")
	parser.print_help()
	sys.exit(0)

# load the object detection network
# raise Exception(sys.argv)
net = jetson.inference.detectNet(opt.network, sys.argv, opt.threshold)
# cam = Camera(0)

# create the camera and display
camera = jetson.utils.gstCamera(opt.width, opt.height, opt.camera)
display = jetson.utils.glDisplay()

INTERESTS = [44, 47, 48, 49, 50]
SAMPLE = [62]

# ser = serial.Serial('/dev/ttyUSB0')

LAST_PING = time.time()

def get_ping():
	"""Return ping command if it has been a few milliseconds"""
	now = time.time()
	if now - LAST_PING > .2:
		return b'ping'
	return None

def move_to_obj_center(obj_center):
	distance = get_ping()

	x, y = obj_center
	if x < 500:
		return b'drive 127 3\n'
	elif x > 800:
		return b'drive 127 1\n'
	elif y > 480:
		return b'stop\n'
	return b'drive 127 0\n'

LAST_SEARCH_ROTATE = time.time()
LAST_SEARCH_DRIVE = time.time()

def search_objects():
	choices = [0, 1]
	now = time.time()
	if (time.time() - LAST_SEARCH_ROTATE) > 3:
		return b'rotate 127 %s' % random.choice(choices)
	return ""

try:
	while display.IsOpen():
		# capture the image
		img, width, height = camera.CaptureRGBA()

		# detect objects in the image (with overlay)
		detections = net.Detect(img, width, height, opt.overlay)

		for detection in detections:
			# 1. Is it an object we want to get?
			# 2. Where is the object relative to the screen?
			# 3. How close to the robot (ping sensor)
			# print(detection.Confidence)
			if detection.ClassID in SAMPLE and detection.Confidence > .50:
				print(move_to_obj_center(detection.Center))

			else:
				print(search_objects())

		# display.RenderOnce(img, width, height)

		# update the title bar
		# display.SetTitle("{:s} | Network {:.0f} FPS".format(opt.network, net.GetNetworkFPS()))

except Exception as e:
	# ser.close()
	raise

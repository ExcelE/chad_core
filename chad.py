#!/usr/bin/python

import jetson.inference
import jetson.utils
import serial
from time import sleep
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
# display = jetson.utils.glDisplay()

INTERESTS = [44, 47, 48, 49, 50]
SAMPLE = [62, 72, 8, 33]

# ser = serial.Serial('/dev/ttyUSB0')

LAST_PING = time.time()

def ask_distance():
	"""Return ping command if it has been a few milliseconds"""
	global LAST_PING
	now = time.time()
	if now - LAST_PING > .2:
		LAST_PING = time.time()
		return b'ping'
	return None

def run_scoop():
	"""
		If the object is in between 30 to 35 cm, then activate the scoop
	"""
	if ask_distance() is not None and 30 < ask_distance() < 35:
		return b'scoop'
	return None
		

def turning(horizontal_value):
	midpoint = 1280/2
	if horizontal_value < midpoint:
		# If it's to the left of the screen, we send the command to move to the right
		# Assumes the left of the image is 0 and the right of the image is 1280)
		speed = 255 * ((midpoint-horizontal_value)/midpoint)
		rotation = 0
		return int(speed), rotation
	else:
		speed = 255 * ((horizontal_value-midpoint)/midpoint)
		rotation = 1
		return int(speed), rotation

def align_to_center_horizontal(obj_center):
	"""
		Three cases:
		1. When the object center is at the center, we move to vertical controls.
		2. When object is at the left of the target zone, we move the bot to the right.
		3. '' '' right, ''' ''' left
	"""

	h_local, w_local = obj_center

	speed, rotation = turning(h_local)
	return b'drive {} {}\n'.format(speed, rotation)


try:
	while True:
		# capture the image
		img, width, height = camera.CaptureRGBA()

		# detect objects in the image (with overlay)
		detections = net.Detect(img, width, height, opt.overlay)
		found = False
		for detection in detections:
			# 1. Is it an object we want to get?
			# 2. Where is the object relative to the screen?
			# 3. How close to the robot (ping sensor)
			if found is False and detection.ClassID in INTERESTS and detection.Confidence > .50:
				
				print(detection.ClassID, align_to_center_horizontal(detection.Center), ask_distance())
				sleep(.1)
				# ser.write(align_to_center_horizontal(detection.Center))


				found = True
			else:
				pass

except Exception as e:
	# ser.close()
	raise

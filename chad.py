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
W_MIDPOINT = int(WIDTH/2)
H_MIDPOINT = int(HEIGHT/2)

# parse the command line
parser = argparse.ArgumentParser(description="Locate objects in a live camera stream using an object detection DNN.", 
						   formatter_class=argparse.RawTextHelpFormatter, epilog=jetson.inference.detectNet.Usage())

parser.add_argument("--network", type=str, default="ssd-mobilenet-v2", help="pre-trained model to load (see below for options)")
parser.add_argument("--overlay", type=str, default="box,labels,conf", help="detection overlay flags (e.g. --overlay=box,labels,conf)\nvalid combinations are:  'box', 'labels', 'conf', 'none'")
parser.add_argument("--threshold", type=float, default=0.5, help="minimum detection threshold to use") 
parser.add_argument("--camera", type=str, default="/dev/video1", help="index of the MIPI CSI camera to use (e.g. CSI camera 0)\nor for VL42 cameras, the /dev/video device to use.\nby default, MIPI CSI camera 0 will be used.")
parser.add_argument("--width", type=int, default=WIDTH, help="desired width of camera stream (default is 1280 pixels)")
parser.add_argument("--height", type=int, default=HEIGHT, help="desired height of camera stream (default is 720 pixels)")

parser.add_argument('--debug', dest='DEBUG', action='store_true')
parser.add_argument('--no-debug', dest='DEBUG', action='store_false')
parser.set_defaults(DEBUG=True)


try:
	opt = parser.parse_known_args()[0]
	DEBUG = opt.DEBUG 
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

if not DEBUG:
	ser = serial.Serial('/dev/ttyUSB0')

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
	distance = ask_distance()
	if distance is not None and 30 < distance < 35:
		return b'scoop'
	return None
		

def turning(horizontal_value):
	midpoint = WIDTH/2
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

	w_local, h_local = obj_center

	speed, direction = turning(w_local)
	return b'rotate {} {}\n'.format(speed, direction)

def drive_opts(vertical_position):
	midpoint = HEIGHT/2
	if vertical_position < midpoint:
		# If it's to the top of the screen, we drive forward
		# Assumes the bottom of the image is 0 and the right of the top is 720)
		speed = 255 * ((midpoint-vertical_position)/midpoint)
		direction = 0
		return int(speed), direction
	else:
		speed = 255 * ((vertical_position-midpoint)/midpoint)
		direction = 1
		return int(speed), direction


def align_to_center_vertical(obj_center):
	"""
		Three cases:
		1. When the object center is at the center, we move start the scooping.
		2. When object is at the too low in the frame, move backwards.
		3. When its too high, move forwards.
	"""

	w_local, h_local = obj_center

	speed, direction = drive_opts(h_local)
	return b'drive {} {}\n'.format(speed, direction)


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
				if DEBUG:
					# print(detection.ClassID, align_to_center_horizontal(detection.Center), ask_distance())
					sleep(.1)
					w, h = detection.Center
					print(detection.Center)
					if h < H_MIDPOINT:
						print("Near the center ", h, detection.Center)

				else:

					w_local, h_local = detection.Center

					# This portion assumes that the target object is centered by the width of the frame.
					# Now we control to move forwards or backwards then pick up the object 
					if (W_MIDPOINT-40) < w_local < (W_MIDPOINT+40):
						# TODO: Need to work on forward/backward movements.
						# Stop whatever commands was sent before.
						if (H_MIDPOINT-20) < h_local < (H_MIDPOINT+20):
							ser.write(b'stop')
							scoop = run_scoop()
							if scoop is not None:
								running = ser.write(scoop)
								
								# We need to block controls until it returns the response scooped.
								while running is not 'scooped':
									sleep(0.1)
						else:
							ser.write(align_to_center_vertical(detection.Center))

					# This portion of the code assumes the object is the side of the frame, so we try to 
					# align as close to the midpoint of the width of the frame
					else:
						ser.write(align_to_center_horizontal(detection.Center))
				found = True
			else:
				pass

except Exception as e:
	if not DEBUG:
		ser.write('stop')
		ser.close()
	raise

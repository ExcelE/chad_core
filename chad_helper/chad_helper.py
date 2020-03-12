
import time, random, curses
from collections import deque
# from manual_controls import Controller

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
		speed = GLOBAL_MOTOR_MAX_SPEED * ((midpoint-horizontal_value)/midpoint)
		rotation = 0
		return int(speed), rotation
	else:
		speed = GLOBAL_MOTOR_MAX_SPEED * ((horizontal_value-midpoint)/midpoint)
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
		speed = GLOBAL_MOTOR_MAX_SPEED * ((midpoint-vertical_position)/midpoint)
		direction = 0
		return int(speed), direction
	else:
		speed = GLOBAL_MOTOR_MAX_SPEED * ((vertical_position-midpoint)/midpoint)
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

class Navigator:
	def __init__(self, serial=None, center=None, name="Unnamed"):
		self.name = name
		self.command_history = deque()
		self.speed = 100
		self.history_size_limit = 20
		self.current_distance = -1
		self.ser = serial
		self.last_ping = 10
		if center is not None:
			self.t_y, self.t_x = center
		self.w_center = None
		self.h_center = None
		# self.Controller = Controller(self.ser)

	# def controller(self):
	# 	pass
		
	def ping(self):
		if (time.time() - self.last_ping) > 0.1:
			self.current_distance = self.send_comm(b"ping")
			self.last_ping = time.time()
		return self.current_distance

	def send_comm(command=None):
		if command is not None and self.ser is not None:
			if len(self.command_history) > self.history_size_limit:
				self.command_history.popleft()
			self.command_history.append(command)
			self.ser.write(command)
		print("DATA SENT: {}".format(command))

	def update_target(self, center, width=None, height=None):
		self.t_y, self.t_x = center
		if width is not None and width > 0:
			self.w_center = int(width / 2) 
		if height is not None and height > 0:
			self.h_center = int(height / 2) 

	def change_speed(self, speed):
		self.speed = speed

	def drive(self, mode=None, rotate=None, drive_setting=None):
		"""
			Mode: 0 -> forward
				  2 -> reverse
		"""
		if mode:
			comm = "{} {} {}\n".format(mode, self.speed, drive_setting).encode()
		if rotate:
			comm = "rotate {} {}\n".format(self.speed, rotate).encode()
		return comm

	def centerize_width(self):
		self.ping()
		start = time.time()
		while time.time() - start < .1:
			error_margin = 20
			if self.t_x > (self.w_center + error_margin):
				self.send_comm(self.rotate_left())
			elif self.t_x < (self.w_center - error_margin):
				self.send_comm(self.rotate_right())
			else:
				return 1 # Object is centered by width within the margin
		self.stop()
		return 0 # Object is not centered yet

	def stop(self):
		self.send_comm(b"stop")

	def forward(self):
		start = time.time()
		while time.time() - start < .2:
			self.send_comm(drive(mode="drive", drive_setting="0"))

	def reverse(self):
		start = time.time()
		while time.time() - start < .2:
			self.send_comm(drive(mode="drive", drive_setting="2"))

	def rotate_left(self):
		self.send_comm(drive(rotate="0"))

	def rotate_right(self):
		self.send_comm(drive(rotate="1"))

	def pick_up(self):
		timer = time.time()
		while not 31 < self.ping() < 37:
			if self.current_distance > 37:
				self.forward()
			else:
				self.reverse()
		while self.ser.write(b"scoop") != "scooped" or time.time() - timer > 90:
			# cancel if it takes more than 90 seconds to respond
			self.t_x = None
			self.t_y = None


	def random_walk(self):
		self.ping()
		start = time.time()

		if self.ser is not None:
			if self.current_distance() < 30:
				self.reverse()
			elif self.current_distance() < 50 and self.t_x is not None:
				# There is an object/obstacle but its not something we want to pick up
				random.choice([self.rotate_left(), self.rotate_right()])
			elif self.current_distance() < 50 and self.t_x:
				# We found the object
				self.pick_up()
			else:
				val = random.choices(
					[0, 1, 2],
					weights=[0.5, 0.25, 0.25])
				if val == 0:
					self.forward()
				elif val == 1:
					self.rotate_left()
				else:
					self.rotate_right()
		else:
			print("Executing random walk")
			
	def blind_run(self):
		if self.ser is not None:
			self.random_walk()

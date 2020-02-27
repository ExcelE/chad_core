
import time, random
from collections import deque


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
	def __init__(self, name="Unnamed", serial, center=None):
		self.name = name
		self.command_history = deque()
		self.speed = 100
		self.history_size_limit = 20
		self.current_distance = -1
		self.ser = serial
		self.last_ping = 10
		if center is not None:
			self.t_y, self.t_x = center

	def ping(self):
		if (self.last_ping - time.time()) > 0.1:
			self.current_distance = self.ser.write(b"ping")
			self.last_ping = time.time()
		return self.current_distance

	def update_target(self, center):
		self.t_y, self.t_x = center

	def update_history(self, command):
		if len(self.command_history) > self.history_size_limit:
			self.command_history.popleft()
		self.command_history.append(command)

	def change_speed(self, speed):
		self.speed = speed

	def drive(self, mode=None, rotate=None, drive_setting=None):
		"""
			Mode: 0 -> forward
					2 -> reverse
		"""
		if mode:
			comm = b"{} {} {}\n".format(mode, self.speed, drive_setting)
		if rotate:
			comm = b"rotate {} {}\n".format(self.speed, rotate)
		self.update_history(comm)
		return comm

	def forward(self):
		start = time.time()
		while time.time() - start < .2:
			ser.write(drive(mode="drive", drive_setting="0"))

	def reverse(self):
		start = time.time()
		while time.time() - start < 0.2:
			ser.write(drive(mode="drive", drive_setting="0"))

	def rotate_left(self):
		start = time.time()
		while time.time() - start < 2:
			ser.write(drive(rotate="0"))

	def rotate_right(self):
		start = time.time()
		while time.time() - start < 2:
			ser.write(drive(rotate="1"))

	def pick_up(self):
		timer = time.time()
		while not 31 < self.ping() < 37:
			if self.current_distance > 37:
				self.forward()
			else:
				self.reverse()
		while ser.write(b"scoop") != "scooped" or time.time() - timer > 90:
			# cancel if it takes more than 90 seconds to respond
			self.t_x = None
			self.t_y = None


	def random_walk(self):
		self.ping()
		start = time.time()


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
			
	def blind_run():
		while True:
			self.random_walk()
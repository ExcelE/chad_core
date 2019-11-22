from nanpy import ArduinoApi, SerialManager, Ultrasonic
from nanpy.serialmanager import SerialManagerError
from time import sleep
import queue

class PingSensor:
    def __init__(self, conn=None, echo_pin=None, trig_pin=None):
        self.conn = None
        self.echo_pin = 10
        self.trig_pin = 9

        if conn is not None:
            self.conn = conn
        if echo_pin is not None:
            self.echo_pin = echo_pin
        if trig_pin is not None:
            self.trig_pin = trig_pin

        self.current_distance = 0
        self.rel_distance = queue.Queue()
        self.queue_size = 20
        
        self.ultrasonic = None

        if self.conn and self.echo_pin and self.trig_pin:
            self.set_up_ultrasonic(conn, echo_pin, trig_pin)

    def set_up_ultrasonic(self, conn, echo_pin=None, trig_pin=None):
        if echo_pin is not None:
            self.echo_pin = echo_pin
        if trig_pin is not None:
            self.trig_pin = trig_pin
        self.ultrasonic = Ultrasonic(self.echo_pin, self.trig_pin, False, connection=conn)

    def calculate_current_dist(self):
        if self.rel_distance.qsize() >= self.queue_size:
            while not self.rel_distance.empty():
                self.current_distance = int((self.current_distance + self.rel_distance.get())/2)
        self.assert_ultrasonic()
        self.rel_distance.put(min(255, max(self.ultrasonic.get_distance(), 0)))

    def distance(self):
        self.calculate_current_dist()
        return self.current_distance

    def assert_ultrasonic(self):
        if self.ultrasonic is None:
            raise self.UltrasonicValidationError("Please setup ultrasonic sensor")


    class UltrasonicValidationError(Exception):
        def __init__(self, message, errors=None):
            super().__init__(message)

# sample = PingSensor()
# connection = SerialManager(device='/dev/ttyACM0')
# a = ArduinoApi(connection=connection)
# sample.set_up_ultrasonic(conn=connection)
# print(sample.echo_pin)
# while True:
#     print(sample.distance())
#     sleep(0.005)

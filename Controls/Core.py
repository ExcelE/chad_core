from nanpy import ArduinoApi, SerialManager, Ultrasonic
from nanpy.serialmanager import SerialManagerError
from time import sleep
import queue
from PingSensor import PingSensor


class Core:
    def __init__(self):
        self.connection = SerialManager(device='/dev/ttyACM0')
        self.a = ArduinoApi(connection=self.connection)
        self.active_pings = []

    def ping_sensor_init(self, echo_pin, trig_pin):
        newPing = self.new_ping(echo_pin, trig_pin)
        if newPing:
            self.active_pings.append(newPing)
        else:
            return False
        
    def new_ping(self, echo_pin, trig_pin):
        for ping in self.active_pings:
            if ping.echo_pin == echo_pin or ping.trig_pin == trig_pin:
                return None
        return PingSensor(self.connection, echo_pin, trig_pin)


p = Core()
p.ping_sensor_init(9, 10)
p.ping_sensor_init(6, 7)

for ping in p.active_pings:
    print(ping.echo_pin, ping.trig_pin)

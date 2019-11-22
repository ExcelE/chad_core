from nanpy import ArduinoApi, SerialManager, Ultrasonic
from nanpy.serialmanager import SerialManagerError
from time import sleep
import queue

trigPin_1 = 9
echoPin_1 = 10

trigPin_2 = 6
echoPin_2 = 7

connection = SerialManager(device='/dev/ttyACM0')

a = ArduinoApi(connection=connection)

ultrasonic = Ultrasonic(echoPin_1, trig_pin_1, False, connection=connection)
rel_distance_hist = queue.Queue()
current_average_dist = 0

def test():
    global current_average_dist
    distance = min(255, max(ultrasonic.get_distance(), 0))

    # if rel_distance_hist.qsize() > 20:
    #     print("Current: {}, Queue size: {}".format(current_average_dist, rel_distance_hist.qsize()))
    #     while not rel_distance_hist.empty():
    #         current_average_dist = int((current_average_dist + int(rel_distance_hist.get()))/2)
    # rel_distance_hist.put(distance)

    print(distance)
    # if 40 < distance < 45:
    # print("Raw Dist: {:6}, Averaged Dist: {:6}, {}".format(distance, current_average_dist, rel_distance_hist.qsize()))

    sleep(0.02)

def run():
    while True:
        test()

try:
    run()
except Exception as e:
    print(e)

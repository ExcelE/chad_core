import cv2, sys
import jetson.inference
import jetson.utils

net = jetson.inference.detectNet('ssd-mobilenet-v2', '0.5')
key = cv2. waitKey(1)
webcam = cv2.VideoCapture(1)

while True:
    try:
        check, frame = webcam.read()
        frame = cv2.flip(frame, -1)
        width  = webcam.get(3)  # float
        height = webcam.get(4) # float

        detections = net.Detect(frame, width, height, "box,labels,conf")
        
        cv2.imshow("Capturing", frame)
        key = cv2.waitKey(1)
        
        if key == ord('q'):
            print("Turning off camera.")
            webcam.release()
            print("Camera off.")
            print("Program ended.")
            cv2.destroyAllWindows()
            break
        
    except(KeyboardInterrupt):
        print("Turning off camera.")
        webcam.release()
        print("Camera off.")
        print("Program ended.")
        cv2.destroyAllWindows()
        break
    
import jetson.inference, jetson.utils, sys

class Vision:
    def __init__(self):
        self.network = "ssd-mobilenet-v2"
        self.threshold = 0.5
        self.width = 1280
        self.height = 720
        self.camera = "0"
        self.overlay = "box,labels,conf"
        self.initialize_network()

    def initialize_network(self, network=None):
        if network is not None:
            self.network = network
        self.net = jetson.inference.detectNet(self.network, sys.argv, self.threshold)

    def visual_process(self, camera=None, display=None):
        if camera is not None:
            self.camera = camera
        if display is not None:
            self.display = display

        self.cam_disp = jetson.utils.gstCamera(self.width, self.height, self.camera)
        self.disp = jetson.utils.glDisplay()

        while self.disp.IsOpen():
            img, width, height = self.cam_disp.CaptureRGBA()
            detections = self.net.Detect(img, width, height, self.overlay)
            print("detected {:d} objects in image".format(len(detections)))

            # for detection in detections:
            #     print(detection)

            # self.disp.RenderOnce(img, width, height)
            self.disp.SetTitle("{:s} | Network {:.0f} FPS".format(self.network, self.net.GetNetworkFPS()))


sl = Vision()
sl.visual_process()
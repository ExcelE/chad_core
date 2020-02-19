# Chad-Core

Object Detection and Distance Estimation Module for Chad Bot

### Description
This repo holds the source code for much of the Object Detection and Distance Estimation functionality for Chad. 

The source code is written and designed for:
1. Jetson TX2
1. Arduino Uno Mega

## How to run:
`python chad.py --camera=/dev/video1`

### Current Functionality Design

The autonomous functionality design is based on NVIDIA's Jetson TX2 platform. We went with the "computing on the edge" approach in our design due to the unreliability of the WiFi network in our campus. Another benefit for using NVIDIA's edge device are the plethora of open source projects by the community. 

We explored the possibility of the using one of our Desktop Server as a command-and-control server and send the video stream captured from the robot and receive the commands from there. The key issue we ran into in the first design was the unreliable connection between the server and the robot. This meant that for this robot to operate autonomously, it would require a WiFi network or an LTE adapter on the design, which would add more latency on processing.

### Autonomous Functionality Design
<img src="CHAD_V2.png" height="300" />

The autonomous functionality heavily relies on image processing to find and detect objects on each frame. Once it finishes compiling the list of objects detected in the frame, the algorithm matches each object if they are present on the object of interests (`INTEREST`).

<img src="assets/detection.png" height="300"/>

`INTERESTS` is a list that matches the class IDs of the detected objects. This is mapped using the `label.py`file to match the name of the object.

<img src="assets/label_maps.png" height="300"/>


### Pre-requisites:
After cloning this repo on the TX2, you must run `./pre-install-script.sh` in order to install the required software packages.
1. `chmod +x pre-install-script.sh`
1. `sudo ./pre-install-script.sh`

### Required Software Packages:
#### Python: (TX2 Optimized)
1. Tensorflow 
1. OpenCV

### Issues:
1. `ld -lGL` not found.
    1. https://devtalk.nvidia.com/default/topic/1051923/jetson-tx2/make-error-usr-bin-ld-cannot-find-lgl-/post/5339745/#5339745
        1. You may have to specify the full path on libGL.so
            1. `sudo ln -sfn libGL.so.1.0.0 /usr/lib/aarch64-linux-gnu/libGL.so`

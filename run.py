import picamera.array
import numpy as np
import socket
import picamera
import sys
from http import client

SERVER_ADDR = '169.254.207.183'

class MotionOutput(picamera.array.PiMotionAnalysis):
    def __init__(self, camera):
        super(MotionOutput, self).__init__(camera)
        self.camera = camera
        self.motion = 0
    
    def analyze(self, a):
        a = np.sqrt(
            np.square(a['x'].astype(np.float)),
            np.square(a['y'].astype(np.float))
        ).clip(0, 255).astype(np.uint8)

        if (a > 80).sum() > 10:
            self.motion += 1
            conn = client.HTTPSConnection(SERVER_ADDR, 7000)
            conn.request("POST", "/intrusion_event")
            conn.getresponse()
            print('Motion detected! %d' % self.motion)


            
class VideoOutput(object):
    def __init__(self, socket):
        self.sock = socket

    def write(self, data):
        self.sock.sendall(data)

    def flush():
        self.sock.close()

        
camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30

video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


video_socket.connect((MACBOOK_ADDR, 8000))

try:
    camera.start_preview()
    camera.start_recording(VideoOutput(video_socket), format='h264', motion_output=MotionOutput(camera))
    while True:
        camera.wait_recording(5)
    camera.stop_recording()
except:
    print(sys.exc_info[0])
    print("Connection reset by peer")
finally:
    video_socket.close()
    camera.close()
    sys.exit(0)
        

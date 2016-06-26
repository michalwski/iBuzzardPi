import picamera.array
import numpy as np
import socket
import picamera
import sys

class MotionOutput(picamera.array.PiMotionAnalysis):
    def __init__(self, camera, socket):
        super(MotionOutput, self).__init__(camera)
        self.camera = camera
        self.motion = 0
        self.sock = socket
        self.target_port = 7000
    
    def analyze(self, a):
        a = np.sqrt(
            np.square(a['x'].astype(np.float)),
            np.square(a['y'].astype(np.float))
        ).clip(0, 255).astype(np.uint8)

        if (a > 60).sum() > 10:
            self.motion += 1
            self.sock.sendall(b'motion')
            # print('Motion detected! %d' % self.motion)

MACBOOK_ADDR = '169.254.207.183'
            
class VideoOutput(object):
    def __init__(self, socket):
        self.sock = socket
        self.target_port = 8000

    def write(self, data):
        self.sock.sendall(data)

    def flush():
        self.sock.close()

        
camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30

video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
motion_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

video_socket.connect((MACBOOK_ADDR, 8000))
motion_socket.connect((MACBOOK_ADDR, 7000))

try:
    camera.start_preview()
    camera.start_recording(VideoOutput(video_socket), format='h264', motion_output=MotionOutput(camera, motion_socket))
    while True:
        camera.wait_recording(5)
    camera.stop_recording()
except:
    print(sys.exc_info[0])
    print("Connection reset by peer")
finally:
    video_socket.close()
    motion_socket.close()
    camera.close()
    sys.exit(0)
        

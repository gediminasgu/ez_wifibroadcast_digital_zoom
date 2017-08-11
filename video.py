import sys
import time
from picamera import PiCamera
from datetime import datetime, timedelta

with PiCamera(sensor_mode=2) as camera: # Set max 
    camera.framerate = 15 # Max allowed fps for that mode
    camera.vflip = True
    camera.start_recording(sys.stdout, "h264", (820, 616))
    time.sleep(15)
    camera.zoom = (0.25,0.25,0.5,0.5)
    time.sleep(15)
    camera.zoom = (0.375,0.375,0.25,0.25)
    time.sleep(15)
    camera.stop_recording()
import sys
import time
from picamera import PiCamera
from datetime import datetime, timedelta
import mavlink

with PiCamera(sensor_mode=2) as camera: # Set max 
    camera.framerate = 15 # Max allowed fps for that mode
    #camera.vflip = True
    camera.start_recording(sys.stdout, "h264", (820, 616))

    mavlink.init()
    currentZoom = 0
    
    while True:
        now = datetime.now()
        if now.second < 2:
            camera.annotate_text = now.strftime('%Y-%m-%d %H:%M:%S')
        else:
            camera.annotate_text = ""


        zoom = mavlink.getZoom()

        if zoom > -1 and zoom != currentZoom:
            currentZoom = zoom
            if zoom == 0:
                camera.zoom = (0,0,1,1)
            
            if zoom == 1:
                camera.zoom = (0.25,0.25,0.5,0.5)

            if zoom == 2:
                camera.zoom = (0.375,0.375,0.25,0.25)
            
    camera.stop_recording()

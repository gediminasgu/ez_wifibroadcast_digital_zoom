import sys
import time
from picamera import PiCamera
from datetime import datetime, timedelta
from mavlink import mavlink

def annotate_with_current_time():
    now = datetime.now()
    if now.second < 2:
        camera.annotate_text = now.strftime('%Y-%m-%d %H:%M:%S')
    else:
        camera.annotate_text = ""

def set_camera_zoom(currentZoom):
    zoom = m.getZoom()

    if zoom > -1 and zoom != currentZoom:
        currentZoom = zoom
        if zoom == 0:
            camera.zoom = (0, 0, 1, 1)

        if zoom == 1:
            camera.zoom = (0.25, 0.25, 0.5, 0.5)

        if zoom == 2:
            camera.zoom = (0.375, 0.375, 0.25, 0.25)

    return currentZoom

m = mavlink()
with PiCamera(sensor_mode=2) as camera: # Set max 
    camera.framerate = 15 # Max allowed fps for that mode
    #camera.vflip = True
    camera.start_recording(sys.stdout, "h264", (820, 616))

    currentZoom = 0
    while True:
        annotate_with_current_time()
        currentZoom = set_camera_zoom(currentZoom)
        time.sleep(0.001)

    camera.stop_recording()

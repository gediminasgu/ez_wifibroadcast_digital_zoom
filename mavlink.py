import sys
import time
import datetime
import os.path
import os
import config

# Sample MSG: fe15 6d01 0124 0e5c 2c06 6c03 cc05 d203 d906 d803 9d06 0000 0000 00a0 de
# fe - start
# 15 - data length 21
# 6d - packet sequence
# 01 - systemID
# 01 - componentID
# 24 - MSG ID: RC_CHANNELS_RAW ( #35 )
# 0e5c 2c06 - time ms from boot
# 6c - port 1 ???
# 00cf -

# For photo camera
# CAMERA_IMAGE_CAPTURED ( #263 )

# $ mkfifo /tmp/telemetry.fifo
# $ sudo ./rx -p 1 -d 2 -b 1 -r 0 -f 64 $NIC | tee /tmp/telemetry.fifo > /dev/null

msg = []
timeset = False
pipe = None
pathToPipe = "/tmp/telemetry.fifo"

def init():
    global pipe
    if os.path.exists(pathToPipe) == False:
        os.mkfifo(pathToPipe, 0777)

    pipe = open(pathToPipe, 'rb')

# Reads MAV link stream and if it finds servo status message (#36) returns according zoom, otherwise returns -1 (unknown)
def getZoom():
    global msg
    global timeset

    if pipe == None:
        return -1

    while True:
        buf = pipe.read(1)

        if len(buf) == 0:
            time.sleep(0.001)
            return -1

        for b in buf:
            if len(msg) > 0:
                msg.append(b)
                if len(msg) == 6:
#                    print str(datetime.datetime.now()) + ": " + str(ord(msg[5])) + " " + str(ord(msg[3]))
                    if  ord(msg[5]) == 36 and ord(msg[1]) == 0x15 and ord(msg[3]) == 0x01 and ord(msg[4]) == 0x01:
                        # keep adding bytes until message will be full
                        continue
                    elif timeset == False and ord(msg[5]) == 2 and ord(msg[3]) == 0x01 and ord(msg[4]) == 0x01:
                        # keep adding bytes until message will be full
                        continue
#                    elif ord(msg[3]) == 71:
#                        print str(ord(msg[5])) + " " + str(ord(msg[3]))
                    else:
                        msg = []

                if len(msg) == 29 and ord(msg[5]) == 36:
                    start = config.ZOOM_CHANNEL_NO * 2 + 8
                    servoPWM = ord(msg[start + 1]) * 256 + ord(msg[start])
                    #print str(servoPWM)
                    msg = []
                    if servoPWM < 1200:
                        return 0
                    if servoPWM > 1400 and servoPWM < 1600:
                        return 1
                    if servoPWM > 1800:
                        return 2                    

                if timeset == False and len(msg) == 20 and ord(msg[5]) == 2:
                    microseconds = ord(msg[13]) * 4294967296 * 16777216 + ord(msg[12]) * 4294967296 * 65536 + ord(msg[11]) * 4294967296 * 256 + ord(msg[10]) * 4294967296 + ord(msg[9]) * 16777216 + ord(msg[8]) * 65536 + ord(msg[7]) * 256 + ord(msg[6])
                    dt = datetime.datetime.fromtimestamp(microseconds / 1000000).strftime('%Y-%m-%d %H:%M:%S.%f')
                    os.system('date --set="%s"' % dt)
                    sys.stderr.write("Time set to: " + dt)
                    timeset = True
                    msg = []

            elif ord(b) == 0xFE:
                    msg = [b]
                    return -1

if __name__ == "__main__":
    init()
    currentZoom = 0
    while True:
        zoom = getZoom()
        if currentZoom != zoom and zoom > -1:
            currentZoom = zoom
            print "Zoom:", currentZoom
        time.sleep(0.001)
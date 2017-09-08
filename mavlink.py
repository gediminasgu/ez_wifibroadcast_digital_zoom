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

class mavlink:

    msg = []
    pipe = None
    pathToPipe = "/tmp/telemetry.fifo"

    # MAVlink message codes
    MAV_SERVO_OUTPUT_RAW = 36
    MAV_SYSTEM_TIME = 2

    def __init__(self):
        if not os.path.exists(self.pathToPipe):
            os.mkfifo(self.pathToPipe, 0777)

        self.pipe = open(self.pathToPipe, 'rb')

    def parse_servo_raw_msg(self, msg):
        start = config.ZOOM_CHANNEL_NO * 2 + 8
        servoPWM = ord(msg[start + 1]) * 256 + ord(msg[start])
        if config.DEBUG:
            print "Zoom servo PWM: {}".format(str(servoPWM))
        if servoPWM > 1350 and servoPWM < 1650:
            return 1
        if servoPWM >= 1650:
            return 2                    

        return 0

    def set_time(self, msg):
        microseconds = ord(msg[13]) * 4294967296 * 16777216 + ord(msg[12]) * 4294967296 * 65536 + ord(msg[11]) * 4294967296 * 256 + ord(msg[10]) * 4294967296 + ord(msg[9]) * 16777216 + ord(msg[8]) * 65536 + ord(msg[7]) * 256 + ord(msg[6])
        
        # Set time only if GPS time from system time differs by 100 seconds
        if abs(microseconds / 1000000 - int(round(time.time()))) > 100:
            dt = datetime.datetime.fromtimestamp(microseconds / 1000000).strftime('%Y-%m-%d %H:%M:%S.%f')
            os.system('date --set="%s"' % dt)
            sys.stderr.write("Time set to: %s" % dt)

    # Parse MAVlink byte stream and if it finds required messages, then it returns result.
    def getZoom(self):
        if self.pipe == None:
            return -1

        while True:
            buf = self.pipe.read(1)

            if len(buf) == 0:
                time.sleep(0.001)
                return -1

            for b in buf:
                if len(self.msg) > 0:
                    self.msg.append(b)
                    if len(self.msg) == 6:
                        if ord(self.msg[3]) == 0x01 and ord(self.msg[4]) == 0x01:
                            if config.DEBUG:
                                print("%s: %s %s" % (datetime.datetime.now(), ord(self.msg[5]), ord(self.msg[3])))
                            if  ord(self.msg[5]) == self.MAV_SERVO_OUTPUT_RAW and ord(self.msg[1]) == 0x15:
                                continue
                            elif config.SET_SYSTEM_TIME and ord(self.msg[5]) == self.MAV_SYSTEM_TIME:
                                continue
                            else:
                                self.msg = []
                        else:
                            self.msg = []

                    if len(self.msg) == 29 and ord(self.msg[5]) == self.MAV_SERVO_OUTPUT_RAW:
                        self.parse_servo_raw_msg(self.msg)
                        self.msg = []

                    if len(self.msg) == 20 and ord(self.msg[5]) == self.MAV_SYSTEM_TIME:
                        self.set_time(self.msg)
                        msg = []

                # Release thread before every message start for other application operations.
                elif ord(b) == 0xFE:
                        msg = [b]
                        return -1

if __name__ == "__main__":
    m = mavlink()
    currentZoom = 0
    while True:
        zoom = m.getZoom()
        if currentZoom != zoom and zoom > -1:
            currentZoom = zoom
            print "Zoom:", currentZoom
        time.sleep(0.001)
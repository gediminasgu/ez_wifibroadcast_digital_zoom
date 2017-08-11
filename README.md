# Digital zoom for ez_wifibroadcast

WORK IN PROGRESS. Replacement for raspivid in ez_wifibroadcast to allow for 4x digital zoom and digital pan with control from Pixhawk. Currently it works only with RasPi camera V2, but easy could be transformed for V1 support (with less zoom).

## Idea
The idea is very simple. It uses max resolution of 3280x2464 (mode #2, see http://picamera.readthedocs.io/en/release-1.13/fov.html#sensor-modes)
to get RAW (not binned) pixels and then resizes picture down to 820x616.

For 2x zoom it uses camera API to crop center of picture to 1640x1232 and again resizes to 820x616. At that zoom digital pan is possible to all directions.

For 4x zoom it crops to 820x616. That is the maximum possible zoom with raw pixels.

## Test it
You can test it piping the output of script to nc utility and sending it over the network to your laptop for view.

To view the video on your laptop you need VLC and the following command:
``
vlc -vvv udp://@:1234 :demux=h264
``

On Raspberry Pi run:
``
python video2.py | nc -p 1904 -u <your computer IP> 1234
``
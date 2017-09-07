# Digital zoom for ez_wifibroadcast

WORK IN PROGRESS. Replacement for raspivid in ez_wifibroadcast to allow for 4x digital zoom and digital pan with control from Pixhawk. It is adapted to RasPi camera V2, but can be used with V1 but zoom will not be so effective.

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

## Use it with your ez-wifibroadcast
To use that script with your ez-wifibroadcast, you need to (all changes are done on TX side):
- copy video.py to your sdcard /root folder
- change one line in your ez-wifibroadcast sdcard /root/.profile file.

Comment this line for later reference:
```
nice -n -9 raspivid -w $WIDTH -h $HEIGHT -fps $FPS -b $BITRATE -g $KEYFRAMERATE -t 0 $EXTRAPARAMS $ANNOTATION -o - | nice -n -9 /root/wifibroadcast/tx_$TXMODE.$VIDEO_WIFI_BITRATE -p 0 -b $VIDEO_BLOCKS -r $VIDEO_FECS -f $VIDEO_BLOCKLENGTH $NICS
```

And add this line:
```
nice -n -9 python /root/video.py | nice -n -9 /root/wifibroadcast/tx_$TXMODE.$VIDEO_WIFI_BITRATE -p 0 -b $VIDEO_BLOCKS -r $VIDEO_FECS -f $VIDEO_BLOCKLENGTH $NICS
```

Put back sdcard to your raspberry and check what you see.

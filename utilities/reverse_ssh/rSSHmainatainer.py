#!/usr/bin/python3


import os
import time
import socket

t=(open('/home/media/docker/setup/config.yaml')).read()[35:38]
while 1:
    if (os.system("curl http://www.fast.com") == 0):
        if((os.popen("ps -aux | grep ssh | grep -v grep").read()).count('ssh -f -N -X -T -R')<1):
            os.system('ssh -f -N -X -T -R 44{}:localhost:22 canlogger@13.71.21.73'.format(t))
        else:
            print("SSH already running")
        time.sleep(5)
    else:
        print("No internet")
    time.sleep(10)


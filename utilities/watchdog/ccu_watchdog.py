#!/usr/bin/python3
import os
import logging
import requests
import time, sys
import subprocess
import socket

from subprocess import Popen, PIPE
from logging.handlers import RotatingFileHandler
CRITICAL_FLAG=False
PROCESS_STATUS=False
PROCESS_ONGOING=False
PROCESS_STOP=False

UPS_IP="192.168.1.113"
UPS_INFO="http://192.168.1.113/cgi-bin/realInfo.cgi"

LOG_FILENAME = '/home/media/docker/logs/watchdog/watchdog.log'

PLC_IP_ADDRESS = "0.0.0.0"
PLC_PORT_NO = 12500
serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSock.bind(("", PLC_PORT_NO))    
serverSock.settimeout(5.0)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=LOG_FILENAME,
                    filemode='a+')
logger = logging.getLogger('my_logger')
handler = RotatingFileHandler(LOG_FILENAME, maxBytes=50*1024*1024, backupCount=10)
logger.addHandler(handler)
logging.debug('CCU WatchDog Started !!!')

errors = { '1' : 'Smoke Detector Alarm' ,
        '2' : 'FDSS Pressure Switch Alarm' ,
        '3' : " Water Level Alarm" ,
        '4' : " Earth Fault Sensing Relay Alarm" ,
        '5' : " Over Current, Short Circuit or Over Temperature (of MCCB Contacts) " ,
        '6' : " Ethernet Relay Sense Alarm " ,
        '7' : " HVAC Feedback Alarm " ,
        '8' : " Under/Over Voltage Protection Alarm " ,
        '9' : " RLB Fan 1 Feedback Alarm " ,
        '10' : " RLB Fan 2 Feedback Alarm " ,
        '11' : " Back Door is open "
}


while True:
  try:
    data, addr = serverSock.recvfrom(1024)
    logging.debug(data)
    if(data[0:11]==b'\x63\x72\x69\x74\x69\x63\x61\x6c\x6d\x73\x67'):
      logging.debug('Category A failure detected !')
      errorcode=errors["{}".format(data[12])]
      logging.debug(errorcode)
      #api goes here
      #CRITICAL_FLAG=True
    if(data[0:16]==b'\x63\x61\x74\x65\x67\x6f\x72\x79\x62\x66\x61\x69\x6c\x75\x72\x65'):
      logging.debug('Category B failure detected !')
      errorcode=errors["{}".format(data[17])]
      logging.debug(errorcode)
    if(data[0:11]==b'\x62\x61\x63\x6b\x20\x64\x6f\x6f\x72\x20\x6f'):
      logging.debug('Back door open !')
      errorcode=errors['11']
      logging.debug(errorcode)
  except socket.timeout: # fail after 1 second of no activity
    print("Didn't receive data! [Timeout]") 

  if CRITICAL_FLAG:
    print("There is a Safety Alarm CCU will not start !")
    logging.debug('There is a Safety Alarm CCU will not start !')
    print("Stoping Docker Container !!!")
    logging.debug('Stoping Docker Container !!!')
    os.system('/home/media/docker/stop-container.sh')
    print("Ubuntu is going to shutdown  !!!")
    logging.debug('Ubuntu is going to Shutdown !!!')
    os.system('systemctl poweroff')
  else:
    processname = 'mediadoc'
    tmp = os.popen("docker ps | grep mediadoc").read()
    proccount = tmp.count(processname)
    if proccount > 0:
      logging.debug('Docker is Running!')
      PROCESS_STATUS=True
      PROCESS_STOP=False
    else:
      logging.debug('Docker Not running')
      PROCESS_STATUS=False
      PROCESS_ONGOING=False

    response = os.system("ping -c 1 " + UPS_IP)
    if response == 0:
      print('UPS is up!')
    else:
      print('UPS is down!')
      logging.debug('UPS is not responding, to verify ping 192.168.1.113 ')
      continue

    print("Checking UPS Bettery Percentage")
    result=requests.get("http://192.168.1.113/cgi-bin/realInfo.cgi")
    data=result.text
    try:
        upsBattery=int(data.splitlines()[10])
        AcInputVoltage=int(data.splitlines()[13])
    except IndexError:
        upsBattery=0
        AcInputVoltage=0
        logging.debug('Exception IndexError Handled')
        continue

    print ("UPS Battery Parcentage %s"%upsBattery)
    logging.debug('UPS Battery Parcentage %s'%upsBattery)
    logging.debug('AC Input Voltage %s'%AcInputVoltage)

    if AcInputVoltage>0:
        logging.debug('AC Power ON')
        if upsBattery>15:
            if (PROCESS_STATUS==False and PROCESS_ONGOING==False):
                logging.debug('Starting Docker Container and all the services')
                os.system('/home/media/docker/start-container.sh')
                PROCESS_ONGOING=True
                #time.sleep(0.01)
        elif upsBattery <= 15:
            print("Waiting UPS to charge !!!")
            logging.debug('Waiting for UPS to charge!')
            #time.sleep(0.01)
    else:
        logging.debug('AC Power OFF')
        if upsBattery>25:
            if (PROCESS_STATUS==False and PROCESS_ONGOING==False):
                print("Starting Docker Container")
                logging.debug('Starting Docker Container and all the services')
                os.system('/home/media/docker/start-container.sh')
                PROCESS_ONGOING=True
                #time.sleep(0.01)
        elif upsBattery<=18:
            print("UPS Battery Remaining Percentage is Very Low !!!")
            logging.debug('UPS Battery Remaining Percentage is Very Low  !!!')
            if upsBattery<=15:
                if (PROCESS_STATUS==True and PROCESS_STOP==False):
                    print("Stoping Docker Container !!!")
                    logging.debug('Stoping Docker Container !!!')
                    os.system('/home/media/docker/stop-container.sh')
                    PROCESS_STOP=True
                    #time.sleep(0.01)
                logging.debug('Docker Container Stopped !!!')
                if upsBattery<=12:
                    print("Ubuntu is going to shutdown  !!!")
                    logging.debug('Ubuntu is going to Shutdown !!!')
                    os.system('systemctl poweroff')

  #time.sleep(0.01)


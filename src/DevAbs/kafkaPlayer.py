#!/usr/bin/env python3

#Authored  by Arvind Umrao< arvindumrao@yahoo.com>
#Date Nov,19, 2018
# This helps in helps in playing back kafka message 

import struct
import json
import logging
import os
import time
import datetime
import shutil
import pathlib


from smqisccuhw.KafkaManager import KafkaManager
 
logging.basicConfig(filename='/var/tmp/test.log',level=logging.DEBUG)
logging.warning('warning')
logging.error( "error")
logging.info( "info")


BLOCKSIZE = 8 

ErrState ={0:"Success",  1:"Failure",  2:"Unknown",  3:"BP Summary bin not found.",  4:"BP Summary bin format is not correct."     }


    
# define a class
class KafkaTest:
    def __init__(self):
        self.data = bytearray()
  
        
    def  PostToKafka(self):
         
        print("PostToKafka")
        kafkaConfig = {
                    'bootstrap_servers': ["127.0.0.1:9092"],
                    'group_id': 'bp_summary',
                    'topics' : []
            }

        global kafka_manager
        kafka_manager = KafkaManager(kafkaConfig)
        #kafka_manager.startConsumer(callback=self.onKafkaMessage)
        
        start = '<'
        end = '>'
#        file = pathlib.Path("./dumptopics.txt")
#        if file.exists ():
#            shutil.copyfile('./dumptopics.txt', './playtopics.txt')  
        
      
        with open('./playtopics.txt') as infile:
            outfile=""
            topic = ""
            copy = False
            for line in infile:
                #print(line)
                if line.startswith("Start"):
                    s = line
                    if(s.find(start) > 0 ):
                       topic= s[s.find(start)+len(start):s.rfind(end)]
                    else:
                       topic = ""
                    copy = True
                elif line.startswith("End"):
                    copy = False
                    #print(topic)
                    #print("topic: {}".format(topic))
                    if topic != "":
                       print(outfile)
                       print(topic)
                       kafka_manager.kafkaProducer(topic, eval(outfile))
                       time.sleep( .1)
                    outfile=""
                    topic = ""
                elif copy:
                    outfile = outfile + line
                    
        return;
       
    

if __name__ == '__main__':
 
    
    p1 = KafkaTest()

    p1.PostToKafka()
    
    time.sleep( 300000000)

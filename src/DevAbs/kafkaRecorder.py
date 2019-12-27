#!/usr/bin/env python3

#Authored  by Arvind Umrao< arvindumrao@yahoo.com>
#Date Nov,19, 2018
# This helps in recording kafka message which later can be playback with kafkaPlayer.py

import struct
import json
import logging
import os
import time
import datetime

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
        self.json=""
       

    def  PostToKafka(self,  err):
         
        print("PostToKafka")
        kafkaConfig = {
                    'bootstrap_servers': ["127.0.0.1:9092"],
                    'group_id': 'bp_summary',
                    'topics' : []
            }

        global kafka_manager
        kafka_manager = KafkaManager(kafkaConfig)
        #kafka_manager.startConsumer(callback=self.onKafkaMessage)
        
        if( err==0):
            
            logPayload = {
                                "application_name": os.path.basename(__file__),
                                "subsystem": "readFromHexFile",
                                "level": "error",
                                "text-message": "Reader error",
                                "json-message": {
                                    "error": ErrState[err] ,
                                        "recovery": "Restarting the DCD Extraction1"
                                    }
                        }
                        
            kafka_manager.sendLog(logPayload)
            
#            print( logPayload)
        
        
        
    def  ReceiverKafka(self):
         
        kafkaConfig = {
                    'bootstrap_servers': ["127.0.0.1:9092"],
                    'group_id': 'BATTERY-ORCHESTRATOR1',
                    'topics' : ["canctlr-to-battorch", "charger-em-data","battorch-to-metrics", "ccuapp-to-log"]
            }

        global kafka_manager
        kafka_manager = KafkaManager(kafkaConfig)
        kafka_manager.startConsumer(callback=self.onKafkaMessage)
        
    
    def WriteToFile(self, topic, data_dict):
        fname = "dumptopics.txt"
        if os.path.isfile(fname):
            # File exists
            with open(fname, 'a+') as outfile:
                #outfile.seek(-1, os.SEEK_END)
                #outfile.seek(0, os.SEEK_END) 
                #outfile.seek(outfile.tell() - 1, os.SEEK_SET)
                #outfile.truncate()
                out = "\nStart of Entry " + str(datetime.datetime.now()) +" <"+ topic + ">\n";
                outfile.write(out)
                outfile.write(data_dict)  
                #json.dump(data_dict, outfile)
                outfile.write('\nEnd of Entry \n')
        else: 
            # Create file
            with open(fname, 'w') as outfile:
                out = "\nStart of Entry " + str(datetime.datetime.now()) +" <"+ topic + ">\n";
                outfile.write(out)
                outfile.write(data_dict)  
                #json.dump(data_dict, outfile)
                outfile.write('\nEnd of Entry \n')
    
        
      
    #@logit
    def onKafkaMessage(self, topic, message):
        
        #print(message)
        print("received: {}".format(message))
        self.WriteToFile(topic, str(message))
        return
        try:
            recordType = message.get('-recordType')
            if recordType == 'DATA':
                    print(": {}".format(message))
            
        except Exception as e:
            print(e)

if __name__ == '__main__':
 
    
    p1 = KafkaTest()
    p1.ReceiverKafka()
    #p1.PostToKafka(0)


    
    time.sleep( 300000000)

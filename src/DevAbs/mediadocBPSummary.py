#!/usr/bin/env python3

#Authored  by Arvind Umrao< arvindumrao@yahoo.com>
#Date Nov,19, 2018
#This class parse the BP Summary bin file. And gives the parsed  data in Json format.
# All the possible test cases are at end of file
#BP Communication Protocol_03.00.00.xls. This communication protocol is for Beta battery packs
#This excel sheet  is in git under src/DevAbs/VENDOR-DOCS
#Right now  check sum of BP summary file is not available, once it is available we will check it.
import struct
import json
import logging
import os
import time

from smqisccuhw.KafkaManager import KafkaManager
 
#logging.warning('warning')
#logging.error( "error")
#logging.info( "info")

BLOCKSIZE = 8 

ErrState ={0:"Success",  1:"Failure",  2:"Unknown",  3:"BP Summary bin not found.",  4:"BP Summary bin format is not correct."     }
    
# define a class
class BPSummary:
    def __init__(self):
        self.data = bytearray()
        self.json={ "download": 1 }
        logging.basicConfig(filename='/ccu/log/mediabp.log',level=logging.INFO)

    def  PostToKafka(self,  err):
         
        print("PostToKafka")
        kafkaConfig = {
                    'bootstrap_servers': ["127.0.0.1:9092"],
                    'group_id': 'bp_summary',
                    'topics' : ["battorch-to-metrics"] #,  "ccuapp-to-log"]
            }

        #global kafka_manager
        kafka_manager = KafkaManager(kafkaConfig)
#        kafka_manager.startConsumer(callback=self.onKafkaMessage)
        
        
        if( err):
            
            logPayload = {
                                "application_name": os.path.basename(__file__),
                                "subsystem": "readFromHexFile",
                                "level": "error",
                                "text-message": "Reader error",
                                "json-message": {
                                    "error": ErrState[err] ,
                                        "recovery": "Restarting the DCD Extraction"
                                    }
                        }
                        
            kafka_manager.sendLog(logPayload)
            
            print( logPayload)
            
        else:
            msg = {
                    "media-time" : kafka_manager.createKfMsgKey(),
                    "media-source" : {
                        "type" : "BP",
                        #"address" : "127.0.0.1"
                    },
                    "media-recordType" : "BP-SUMMARY-DATA",
                    "media-txIdKey" : kafka_manager.createTxIdKey(),
                    "@version" : "1",
                    "media-data" : {
                        "BPSummary" : self.json
                    }
                }
            print(msg) 
            kafka_manager.kafkaProducer('battorch-to-metrics', msg)
        
        
        #sys.exit(0)
        time.sleep(0.1)

if __name__ == '__main__':
    
    p1 = BPSummary()
    p1.PostToKafka(1)

    time.sleep( 300)

#!/usr/bin/env python3

#Authored  by Arvind Umrao< arvindumrao@yahoo.com>
#Date Nov,19, 2018
#This class parse the BP info bin file. And gives the parsed  data in Json format.
# All the possible test cases are at end of file
#BP Communication Protocol_03.00.00.xls. This communication protocol is for Beta battery packs
#This excel sheet  is in git under src/DevAbs/VENDOR-DOCS
#Right now  check sum of BP info file is not available, once it is available we will check it.
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

ErrState ={0:"Success",  1:"Failure",  2:"Unknown",  3:"BP Info bin not found.",  4:"BP Info bin format is not correct."     }
    
# define a class
class BPInfo:
    def __init__(self):
        self.data = bytearray()
        self.json=""
        logging.basicConfig(filename='/ccu/log/mediadocbp.log',level=logging.INFO)
        
    def ByteArrayToAnscii(self, bytarr):
        s = ''
        for x in bytarr:
            if ( x == 0):
                 s = s+ '0'
            else:   
                 s= s + chr(x)
        return s
    
      # Open file, Read it and check the file format
      # Return Succes/Failure
    def openBPBin(self,  file ):
        count = 1 
        try:
             with open( file, 'rb') as afile:
                buf = afile.read(BLOCKSIZE)
                while len(buf) > 0:
                    if(count != buf[0]):
                        print("BP info file is currupted: "  + file )
                        logging.error("BP info file is currupted: "  + file )
                        return 4
                         
                    self.data= self.data + buf[1:]
                    #print(buf.hex())
                    count=count+1;
                    buf = afile.read(BLOCKSIZE)
        except:
            print( "BP info file is not available: " + file  )
            logging.error( "BP info file is not available: " + file)
            return 3
            
            if ( count != 37 ):
                print("BP info file is currupted")
                logging.error( "BP info file is currupted")
                return 4
        return 0
       
    # Parse the binary file as per Communication Protocol_03.00.00.xls
    # Return Succes/Failure   
    def parseBPBin(self ):
        try:
             
            baseformat = '< 3s 20s 3s 3s H 16s B 17s 3s 3s 3s 3s 17s 3s 3s 3s 3s 17s 3s 3s 3s 3s 17s 102x H'
            Version,  BP_Serialnum,  Installation_Date,  Full_Charge_Date,   Battery_Capacity, \
            Resistance_Cell, BP_Internal_Resistance, \
            SCU_SerialNO, SCU_Bootloader_ver, SCU_Firmware_ver,  SCU_Hardware_ver, SCU_Communication_ver,  \
            BMS_SerialNO, BMS_Bootloader_ver, BMS_Firmware_ver,  BMS_Hardware_ver, BMS_Communication_ver,  \
            TIU_SerialNO, TIU_Bootloader_ver, TIU_Firmware_ver,  TIU_Hardware_ver, TIU_Communication_ver,  \
            RFID,  checksum \
            =struct.unpack(baseformat, self.data[0:256])
        except:
            print( "BP Info bin file format is not correct." ) 
            logging.error( "BP Info bin file format is not correct.")
            return 4
        xJson= {
		
		"Version": str( int(Version[0:1].hex(), 16)) + "." +  str(int(Version[1:2].hex(), 16)) + "." + str(int(Version[2:3].hex(), 16)),
		"BP_Serialnum": self.ByteArrayToAnscii(BP_Serialnum), 
		"Installation_Date": str( int(Installation_Date[0:1].hex(), 16)) + "-" +  str(int(Installation_Date[1:2].hex(), 16)) + "-" + str(int(Installation_Date[2:3].hex(), 16)),
		"Full_Charge_Date": str( int(Full_Charge_Date[0:1].hex(), 16)) + "-" +  str(int(Full_Charge_Date[1:2].hex(), 16)) + "-" + str(int(Full_Charge_Date[2:3].hex(), 16)),
		"Battery_Capacity": Battery_Capacity * 0.1,
		"Resistance_Cell[1]": round(int.from_bytes(Resistance_Cell[0:1], byteorder='little', signed=False) * 0.01, 2),
		"Resistance_Cell[2]": round(int.from_bytes(Resistance_Cell[1:2], byteorder='little', signed=False) * 0.01, 2),
		"Resistance_Cell[3]": round(int.from_bytes(Resistance_Cell[2:3], byteorder='little', signed=False) * 0.01, 2),
		"Resistance_Cell[4]": round(int.from_bytes(Resistance_Cell[3:4], byteorder='little', signed=False) * 0.01, 2),
		"Resistance_Cell[5]": round(int.from_bytes(Resistance_Cell[4:5], byteorder='little', signed=False) * 0.01, 2),
		"Resistance_Cell[6]": round(int.from_bytes(Resistance_Cell[5:6], byteorder='little', signed=False) * 0.01, 2),
		"Resistance_Cell[7]": round(int.from_bytes(Resistance_Cell[6:7], byteorder='little', signed=False) * 0.01, 2),
		"Resistance_Cell[8]": round(int.from_bytes(Resistance_Cell[7:8], byteorder='little', signed=False) * 0.01, 2),
		"Resistance_Cell[9]": round(int.from_bytes(Resistance_Cell[8:9], byteorder='little', signed=False) * 0.01, 2),
		"Resistance_Cell[10]": round(int.from_bytes(Resistance_Cell[9:10], byteorder='little', signed=False) * 0.01, 2),
		"Resistance_Cell[11]": round(int.from_bytes(Resistance_Cell[10:11], byteorder='little', signed=False) * 0.01, 2),
		"Resistance_Cell[12]": round(int.from_bytes(Resistance_Cell[11:12], byteorder='little', signed=False) * 0.01, 2),
		"Resistance_Cell[13]": round(int.from_bytes(Resistance_Cell[12:13], byteorder='little', signed=False) * 0.01, 2),
		"Resistance_Cell[14]": round(int.from_bytes(Resistance_Cell[13:14], byteorder='little', signed=False) * 0.01, 2),
		"Resistance_Cell[15]": round(int.from_bytes(Resistance_Cell[14:15], byteorder='little', signed=False) * 0.01, 2),
		"Resistance_Cell[16]": round(int.from_bytes(Resistance_Cell[15:16], byteorder='little', signed=False) * 0.01, 2),
		"BP_Internal_Resistance": BP_Internal_Resistance * 0.1,
		"SCU_SerialNO": self.ByteArrayToAnscii(SCU_SerialNO), 
		"SCU_Bootloader_ver": str( int(SCU_Bootloader_ver[0:1].hex(), 16)) + "." +  str(int(SCU_Bootloader_ver[1:2].hex(), 16)) + "." + str(int(SCU_Bootloader_ver[2:3].hex(), 16)),
		"SCU_Firmware_ver": str( int(SCU_Firmware_ver[0:1].hex(), 16)) + "." +  str(int(SCU_Firmware_ver[1:2].hex(), 16)) + "." + str(int(SCU_Firmware_ver[2:3].hex(), 16)),
		"SCU_Hardware_ver": str( int(SCU_Hardware_ver[0:1].hex(), 16)) + "." +  str(int(SCU_Hardware_ver[1:2].hex(), 16)) + "." + str(int(SCU_Hardware_ver[2:3].hex(), 16)),
		"SCU_Communication_ver": str( int(SCU_Communication_ver[0:1].hex(), 16)) + "." +  str(int(SCU_Communication_ver[1:2].hex(), 16)) + "." + str(int(SCU_Communication_ver[2:3].hex(), 16)),
		"BMS_SerialNO": self.ByteArrayToAnscii(BMS_SerialNO), 
		"BMS_Bootloader_ver": str( int(BMS_Bootloader_ver[0:1].hex(), 16)) + "." +  str(int(BMS_Bootloader_ver[1:2].hex(), 16)) + "." + str(int(BMS_Bootloader_ver[2:3].hex(), 16)),
		"BMS_Firmware_ver": str( int(BMS_Firmware_ver[0:1].hex(), 16)) + "." +  str(int(BMS_Firmware_ver[1:2].hex(), 16)) + "." + str(int(BMS_Firmware_ver[2:3].hex(), 16)),
		"BMS_Hardware_ver": str( int(BMS_Hardware_ver[0:1].hex(), 16)) + "." +  str(int(BMS_Hardware_ver[1:2].hex(), 16)) + "." + str(int(BMS_Hardware_ver[2:3].hex(), 16)),
		"BMS_Communication_ver": str( int(BMS_Communication_ver[0:1].hex(), 16)) + "." +  str(int(BMS_Communication_ver[1:2].hex(), 16)) + "." + str(int(BMS_Communication_ver[2:3].hex(), 16)),
		"TIU_SerialNO": self.ByteArrayToAnscii(TIU_SerialNO), 
		"TIU_Bootloader_ver": str( int(TIU_Bootloader_ver[0:1].hex(), 16)) + "." +  str(int(TIU_Bootloader_ver[1:2].hex(), 16)) + "." + str(int(TIU_Bootloader_ver[2:3].hex(), 16)),
		"TIU_Firmware_ver": str( int(TIU_Firmware_ver[0:1].hex(), 16)) + "." +  str(int(TIU_Firmware_ver[1:2].hex(), 16)) + "." + str(int(TIU_Firmware_ver[2:3].hex(), 16)),
		"TIU_Hardware_ver": str( int(TIU_Hardware_ver[0:1].hex(), 16)) + "." +  str(int(TIU_Hardware_ver[1:2].hex(), 16)) + "." + str(int(TIU_Hardware_ver[2:3].hex(), 16)),
		"TIU_Communication_ver": str( int(TIU_Communication_ver[0:1].hex(), 16)) + "." +  str(int(TIU_Communication_ver[1:2].hex(), 16)) + "." + str(int(TIU_Communication_ver[2:3].hex(), 16)),
		"RFID": self.ByteArrayToAnscii(RFID)
        }
        
        yjson = json.dumps(xJson)
        self.json = yjson
        logging.info(yjson)
        print(yjson)
        return 0
        
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
            
#            print( logPayload)
            
        else:
            msg = {
                    "mediadoc-time" : kafka_manager.createKfMsgKey(),
                    "mediadoc-source" : {
                        "type" : "BP",
                        #"address" : "127.0.0.1"
                    },
                    "mediadoc-recordType" : "BP-CONFIGURATION-DATA",
                    "mediadoc-txIdKey" : kafka_manager.createTxIdKey(),
                    "@version" : "1",
                    "mediadoc-data" : {
                    "BPInfo" : self.json
                    }
                }
            
            kafka_manager.kafkaProducer('battorch-to-metrics', msg)
        
        
        #sys.exit(0)
        time.sleep(0.1)
    
if __name__ == '__main__':

    #Test Case begings
    binFile = '/var/tmp/20181113-0017.infobin'
    print(binFile)
    p1 = BPInfo()

    result = p1.openBPBin(binFile)

    if( result):
        print( ErrState[result] + " : " +binFile )
    else:
        parseResult = p1.parseBPBin()
        p1.PostToKafka( parseResult)
        if( parseResult):
            print( ErrState[parseResult] + " : " +binFile )
        else:
            print( ErrState[parseResult] + " : " +binFile )

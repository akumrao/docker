#!/usr/bin/env python3

#Authored  by Arvind Umrao< arvindumrao@yahoo.com>
#Date Nov,19, 2018
#This class parse the BP Settings bin file. And gives the parsed  data in Json format.
# All the possible test cases are at end of file
#BP Communication Protocol_03.00.00.xls. This communication protocol is for Beta battery packs
#This excel sheet  is in git under src/DevAbs/VENDOR-DOCS
#Right now  check sum of BP Settings file is not available, once it is available we will check it.
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

ErrState ={0:"Success",  1:"Failure",  2:"Unknown",  3:"BP Settings bin not found.",  4:"BP Settings bin format is not correct."     }


    
# define a class
class BPSetting:
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
                        print("BP Settings file is currupted: "  + file )
                        logging.error("BP Settings file is currupted: "  + file )
                        return 4
                         
                    self.data= self.data + buf[1:]
                    #print(buf.hex())
                    count=count+1;
                    buf = afile.read(BLOCKSIZE)
        except:
            print( "BP Summary file is not available: " + file  )
            logging.error( "BP Settings file is not available: " + file)  
            return 3
            
            if ( count != 37 ):
                print("BP Summary file is currupted")
                logging.error( "BP Settings file is currupted")  
                return 4
        return 0
       
    # Parse the binary file as per Communication Protocol_03.00.00.xls
    # Return Succes/Failure   
    def parseBPBin(self ):
        try:

            baseformat = '< b b b b H H H H H H H H b B B 3s H H B B 16s 16s 16s 16s H H H b b H H H H H b b H H H b b H H 3s 3s 3s 3s H H 3s H 3s H 3s b 3s b 3s 10s 20s H H b b b b b H 3s 3s 3s 3s 3s H 3s 28x H'
            Cut_off_Cell_High_Temperature, Resume_Cell_High_Temperature, Cut_off_Cell_Low_Temperature, \
            Resume_Cell_Low_Temperature, Cell_Over_Voltage, Cell_Under_Voltage, \
            Constant_Current_Phase_End_Max_Voltage, Constant_Current_Phase_End_Avg_Voltage, Current_Request_Constant_Current_Phase, \
            Constant_Voltage_Phase_End_Max_Voltage, Constant_Voltage_Phase_End_Avg_Voltage, Constant_Voltage_Phase_End_Current, \
            Charge_Start_Temperature, Tolerance_band_for_Charge_Start_Temperature, Enable_Disable, \
            Duration, Cell_Voltage_Greater_than_Equal_to, Cell_Deviation, \
            Charge, Discharge, Drive_Current, \
            Regen_Current, Under_Voltage_limits_wrt_Temperature, Over_Voltage_limits_wrt_Temperature, \
            Economy_Mode_Drive_Current_Limit, Economy_Mode_Regen_Current_Limit, Economy_Mode_SoC, \
            Economy_Mode_Maximum_Cell_Temperature, Economy_Mode_Minimum_Cell_Temperature, Economy_Mode_Maximum_Cell_Voltage, \
            Economy_Mode_Minimum_Cell_Voltage, Limphome_Mode_Drive_Current_Limit,  Limphome_Mode_Regen_Current_Limit, \
            Limphome_Mode_SoC, Limphome_Mode_Maximum_Cell_Temperature, Limphome_Mode_Minimum_Cell_Temperature, \
            Limphome_Mode_Maximum_Cell_Voltage, Limphome_Mode_Minimum_Cell_Voltage, Stop_SoC, \
            Stop_Maximum_Cell_Temperature, Stop_Minimum_Cell_Temperature, Stop_Maximum_Cell_Voltage, \
            Stop_Minimum_Cell_Voltage, Drive_Data_Store_rate, Total_Drive_Hours, \
            Idle_Data_Store_rate, Total_Idle_Hours, Number_of_History_Cycles, \
            Battery_SoC, Duration_for_checking_the_Battery_SoC, Battery_Maximum_Cell_Voltage, \
            Duration_for_checking_the_Battery_Maximum_Cell_Voltage, Battery_Minimum_Cell_Voltage, Duration_for_checking_the_Battery_Minimum_Cell_Voltage, \
            Battery_Maximum_Cell_Temperature, Duration_for_checking_the_Battery_Maximum_Cell_Temperature, Battery_Minimum_Cell_Temperature, \
            Duration_for_checking_the_Battery_Minimum_Cell_Temperature, Battery_Temperature_Look_up, Battery_Capacity_percentage_wrt_Temperature_Lookup, \
            Battery_Capacity, Battery_Usable_Capacity, Cut_off_Battery_positive_High_Temperature, \
            Resume_Battery_positive_High_Temperature, Economy_Mode_Maximum_SCU_Temperature, Limphome_Mode_Maximum_SCU_Temperature, \
            Stop_Maximum_SCU_Temperature, Supply_Voltage, Duration_for_checking_the_Supply_Voltage, \
            Idle_Time_Check_duration, Drive_Charge_Data_Transfer_rate, Idle_Data_Transfer_rate,  \
            Topup_Charge_time_interval, Correction_Factor, Correction_Duration, Checksum \
            =struct.unpack(baseformat, self.data[0:256])
        except:
            print( "BP Settings bin file format is not correct." ) 
            logging.error( "BP Settings bin file format is not correct.")  
            return 4
        xJson= {
		"Cut_off_Cell_High_Temperature": Cut_off_Cell_High_Temperature * 1,
		"Resume_Cell_High_Temperature": Resume_Cell_High_Temperature * 1,
		"Cut_off_Cell_Low_Temperature": Cut_off_Cell_Low_Temperature * 1,
		"Resume_Cell_Low_Temperature": Resume_Cell_Low_Temperature * 1,
		"Cell_Over_Voltage": Cell_Over_Voltage * 0.001,
		"Cell_Under_Voltage": Cell_Under_Voltage * 0.001,
		"Constant_Current_Phase_End_Max_Voltage": Constant_Current_Phase_End_Max_Voltage * 0.001,
		"Constant_Current_Phase_End_Avg_Voltage": Constant_Current_Phase_End_Avg_Voltage * 0.001,
		"Current_Request_Constant_Current_Phase": Current_Request_Constant_Current_Phase * 0.1,
		"Constant_Voltage_Phase_End_Max_Voltage": Constant_Voltage_Phase_End_Max_Voltage * 0.001,
		"Constant_Voltage_Phase_End_Avg_Voltage": Constant_Voltage_Phase_End_Avg_Voltage * 0.001,
		"Constant_Voltage_Phase_End_Current": Constant_Voltage_Phase_End_Current * 0.1,
		"Charge_Start_Temperature": Charge_Start_Temperature * 1,
		"Tolerance_band_for_Charge_Start_Temperature": Tolerance_band_for_Charge_Start_Temperature * 1,
		"Enable_Disable": Enable_Disable * 1,
		"Duration": str( int(Duration[0:1].hex(), 16)) + ":" +  str(int(Duration[1:2].hex(), 16)) + ":" + str(int(Duration[2:3].hex(), 16)),
		"Cell_Voltage_Greater_than_Equal_to": Cell_Voltage_Greater_than_Equal_to * 0.001,
		"Cell_Deviation": Cell_Deviation * 0.001,
		"Charge": Charge * 1,
		"Discharge": Discharge * 1,
		"Drive_Current[0]": int.from_bytes(Drive_Current[0:2], byteorder='little', signed=False) * 0.1,
		"Drive_Current[1]": int.from_bytes(Drive_Current[2:4], byteorder='little', signed=False) * 0.1,
		"Drive_Current[2]": int.from_bytes(Drive_Current[4:6], byteorder='little', signed=False) * 0.1,
		"Drive_Current[3]": int.from_bytes(Drive_Current[6:8], byteorder='little', signed=False) * 0.1,
		"Drive_Current[4]": int.from_bytes(Drive_Current[8:10], byteorder='little', signed=False) * 0.1,
		"Drive_Current[5]": int.from_bytes(Drive_Current[10:12], byteorder='little', signed=False) * 0.1,
		"Drive_Current[6]": int.from_bytes(Drive_Current[12:14], byteorder='little', signed=False) * 0.1,
		"Drive_Current[7]": int.from_bytes(Drive_Current[14:16], byteorder='little', signed=False) * 0.1,
		"Regen_Current[0]": int.from_bytes(Regen_Current[0:2], byteorder='little', signed=False) * 0.1,
		"Regen_Current[1]": int.from_bytes(Regen_Current[2:4], byteorder='little', signed=False) * 0.1,
		"Regen_Current[2]": int.from_bytes(Regen_Current[4:6], byteorder='little', signed=False) * 0.1,
		"Regen_Current[3]": int.from_bytes(Regen_Current[6:8], byteorder='little', signed=False) * 0.1,
		"Regen_Current[4]": int.from_bytes(Regen_Current[8:10], byteorder='little', signed=False) * 0.1,
		"Regen_Current[5]": int.from_bytes(Regen_Current[10:12], byteorder='little', signed=False) * 0.1,
		"Regen_Current[6]": int.from_bytes(Regen_Current[12:14], byteorder='little', signed=False) * 0.1,
		"Regen_Current[7]": int.from_bytes(Regen_Current[14:16], byteorder='little', signed=False) * 0.1,
		"Under_Voltage_limits_wrt_Temperature[0]": int.from_bytes(Under_Voltage_limits_wrt_Temperature[0:2], byteorder='little', signed=False) * 0.001,
		"Under_Voltage_limits_wrt_Temperature[1]": int.from_bytes(Under_Voltage_limits_wrt_Temperature[2:4], byteorder='little', signed=False) * 0.001,
		"Under_Voltage_limits_wrt_Temperature[2]": int.from_bytes(Under_Voltage_limits_wrt_Temperature[4:6], byteorder='little', signed=False) * 0.001,
		"Under_Voltage_limits_wrt_Temperature[3]": int.from_bytes(Under_Voltage_limits_wrt_Temperature[6:8], byteorder='little', signed=False) * 0.001,
		"Under_Voltage_limits_wrt_Temperature[4]": int.from_bytes(Under_Voltage_limits_wrt_Temperature[8:10], byteorder='little', signed=False) * 0.001,
		"Under_Voltage_limits_wrt_Temperature[5]": int.from_bytes(Under_Voltage_limits_wrt_Temperature[10:12], byteorder='little', signed=False) * 0.001,
		"Under_Voltage_limits_wrt_Temperature[6]": int.from_bytes(Under_Voltage_limits_wrt_Temperature[12:14], byteorder='little', signed=False) * 0.001,
		"Under_Voltage_limits_wrt_Temperature[7]": int.from_bytes(Under_Voltage_limits_wrt_Temperature[14:16], byteorder='little', signed=False) * 0.001,
		"Over_Voltage_limits_wrt_Temperature[0]": int.from_bytes(Over_Voltage_limits_wrt_Temperature[0:2], byteorder='little', signed=False) * 0.001,
		"Over_Voltage_limits_wrt_Temperature[1]": int.from_bytes(Over_Voltage_limits_wrt_Temperature[2:4], byteorder='little', signed=False) * 0.001,
		"Over_Voltage_limits_wrt_Temperature[2]": int.from_bytes(Over_Voltage_limits_wrt_Temperature[4:6], byteorder='little', signed=False) * 0.001,
		"Over_Voltage_limits_wrt_Temperature[3]": int.from_bytes(Over_Voltage_limits_wrt_Temperature[6:8], byteorder='little', signed=False) * 0.001,
		"Over_Voltage_limits_wrt_Temperature[4]": int.from_bytes(Over_Voltage_limits_wrt_Temperature[8:10], byteorder='little', signed=False) * 0.001,
		"Over_Voltage_limits_wrt_Temperature[5]": int.from_bytes(Over_Voltage_limits_wrt_Temperature[10:12], byteorder='little', signed=False) * 0.001,
		"Over_Voltage_limits_wrt_Temperature[6]": int.from_bytes(Over_Voltage_limits_wrt_Temperature[12:14], byteorder='little', signed=False) * 0.001,
		"Over_Voltage_limits_wrt_Temperature[7]": int.from_bytes(Over_Voltage_limits_wrt_Temperature[14:16], byteorder='little', signed=False) * 0.001,
		"Economy_Mode_Drive_Current_Limit": Economy_Mode_Drive_Current_Limit * 0.1,
		"Economy_Mode_Regen_Current_Limit": Economy_Mode_Regen_Current_Limit * 0.1,
		"Economy_Mode_SoC": Economy_Mode_SoC * 0.1,
		"Economy_Mode_Maximum_Cell_Temperature": Economy_Mode_Maximum_Cell_Temperature * 1,
		"Economy_Mode_Minimum_Cell_Temperature": Economy_Mode_Minimum_Cell_Temperature * 1,
		"Economy_Mode_Maximum_Cell_Voltage": Economy_Mode_Maximum_Cell_Voltage * 0.001,
		"Economy_Mode_Minimum_Cell_Voltage": Economy_Mode_Minimum_Cell_Voltage * 0.001,
		"Limphome_Mode_Drive_Current_Limit": Limphome_Mode_Drive_Current_Limit * 0.1,
		"Limphome_Mode_Regen_Current_Limit": Limphome_Mode_Regen_Current_Limit * 0.1,
		"Limphome_Mode_SoC": Limphome_Mode_SoC * 0.1,
		"Limphome_Mode_Maximum_Cell_Temperature": Limphome_Mode_Maximum_Cell_Temperature * 1,
		"Limphome_Mode_Minimum_Cell_Temperature": Limphome_Mode_Minimum_Cell_Temperature * 1,
		"Limphome_Mode_Maximum_Cell_Voltage": Limphome_Mode_Maximum_Cell_Voltage * 0.001,
		"Limphome_Mode_Minimum_Cell_Voltage": Limphome_Mode_Minimum_Cell_Voltage * 0.001,
		"Stop_SoC,": Stop_SoC * 0.1,
		"Stop_Maximum_Cell_Temperature": Stop_Maximum_Cell_Temperature * 1,
		"Stop_Minimum_Cell_Temperature": Stop_Minimum_Cell_Temperature * 1,
		"Stop_Maximum_Cell_Voltage": Stop_Maximum_Cell_Voltage * 0.001,
		"Stop_Minimum_Cell_Voltage": Stop_Minimum_Cell_Voltage * 0.001,
                "Drive_Data_Store_rate": str( int(Drive_Data_Store_rate[0:1].hex(), 16)) + ":" +  str(int(Drive_Data_Store_rate[1:2].hex(), 16)) + ":" + str(int(Drive_Data_Store_rate[2:3].hex(), 16)),
                "Total_Drive_Hours": str( int(Total_Drive_Hours[0:1].hex(), 16)) + ":" +  str(int(Total_Drive_Hours[1:2].hex(), 16)) + ":" + str(int(Total_Drive_Hours[2:3].hex(), 16)),
                "Idle_Data_Store_rate": str( int(Idle_Data_Store_rate[0:1].hex(), 16)) + ":" +  str(int(Idle_Data_Store_rate[1:2].hex(), 16)) + ":" + str(int(Idle_Data_Store_rate[2:3].hex(), 16)),
                "Total_Idle_Hours": str( int(Total_Idle_Hours[0:1].hex(), 16)) + ":" +  str(int(Total_Idle_Hours[1:2].hex(), 16)) + ":" + str(int(Total_Idle_Hours[2:3].hex(), 16)),
		"Number_of_History_Cycles": Number_of_History_Cycles * 1,
		"Battery_SoC": Battery_SoC * 0.1,
		"Duration_for_checking_the_Battery_SoC": str( int(Duration_for_checking_the_Battery_SoC[0:1].hex(), 16)) + ":" +  str(int(Duration_for_checking_the_Battery_SoC[1:2].hex(), 16)) + ":" + str(int(Duration_for_checking_the_Battery_SoC[2:3].hex(), 16)),
		"Battery_Maximum_Cell_Voltage": Battery_Maximum_Cell_Voltage * 0.001,
		"Duration_for_checking_the_Battery_Maximum_Cell_Voltage": str( int(Duration_for_checking_the_Battery_Maximum_Cell_Voltage[0:1].hex(), 16)) + ":" +  str(int(Duration_for_checking_the_Battery_Maximum_Cell_Voltage[1:2].hex(), 16)) + ":" + str(int(Duration_for_checking_the_Battery_Maximum_Cell_Voltage[2:3].hex(),16)),
		"Battery_Minimum_Cell_Voltage": Battery_Minimum_Cell_Voltage * 0.001,
		"Duration_for_checking_the_Battery_Minimum_Cell_Voltage": str( int(Duration_for_checking_the_Battery_Minimum_Cell_Voltage[0:1].hex(), 16)) + ":" +  str(int(Duration_for_checking_the_Battery_Minimum_Cell_Voltage[1:2].hex(), 16)) + ":" + str(int(Duration_for_checking_the_Battery_Minimum_Cell_Voltage[2:3].hex(), 16)),
		"Battery_Maximum_Cell_Temperature": Battery_Maximum_Cell_Temperature * 1,
		"Duration_for_checking_the_Battery_Maximum_Cell_Temperature": str( int(Duration_for_checking_the_Battery_Maximum_Cell_Temperature[0:1].hex(), 16)) + ":" +  str(int(Duration_for_checking_the_Battery_Maximum_Cell_Temperature[1:2].hex(), 16)) + ":" + str(int(Duration_for_checking_the_Battery_Maximum_Cell_Temperature[2:3].hex(), 16)),
		"Battery_Minimum_Cell_Temperature": Battery_Minimum_Cell_Temperature * 1,
		"Duration_for_checking_the_Battery_Minimum_Cell_Temperature": str( int(Duration_for_checking_the_Battery_Minimum_Cell_Temperature[0:1].hex(), 16)) + ":" +  str(int(Duration_for_checking_the_Battery_Minimum_Cell_Temperature[1:2].hex(), 16)) + ":" + str(int(Duration_for_checking_the_Battery_Minimum_Cell_Temperature[2:3].hex(), 16)),
		"Battery_Temperature_Look_up[0]": int.from_bytes(Battery_Temperature_Look_up[0:2], byteorder='little', signed=False) * 1,
		"Battery_Temperature_Look_up[1]": int.from_bytes(Battery_Temperature_Look_up[2:4], byteorder='little', signed=False) * 1,
		"Battery_Temperature_Look_up[2]": int.from_bytes(Battery_Temperature_Look_up[4:6], byteorder='little', signed=False) * 1,
		"Battery_Temperature_Look_up[3]": int.from_bytes(Battery_Temperature_Look_up[6:8], byteorder='little', signed=False) * 1,
		"Battery_Temperature_Look_up[4]": int.from_bytes(Battery_Temperature_Look_up[8:10], byteorder='little', signed=False) * 1,
		"Battery_Temperature_Look_up[5]": int.from_bytes(Battery_Temperature_Look_up[10:12], byteorder='little', signed=False) * 1,
		"Battery_Temperature_Look_up[6]": int.from_bytes(Battery_Temperature_Look_up[12:14], byteorder='little', signed=False) * 1,
		"Battery_Temperature_Look_up[7]": int.from_bytes(Battery_Temperature_Look_up[14:16], byteorder='little', signed=False) * 1,
		"Battery_Temperature_Look_up[8]": int.from_bytes(Battery_Temperature_Look_up[16:18], byteorder='little', signed=False) * 1,
		"Battery_Temperature_Look_up[9]": int.from_bytes(Battery_Temperature_Look_up[18:20], byteorder='little', signed=False) * 1,
		"Battery_Capacity_percentage_wrt_Temperature_Lookup[0]": int.from_bytes(Battery_Capacity_percentage_wrt_Temperature_Lookup[0:2], byteorder='little', signed=False) * 0.01,
		"Battery_Capacity_percentage_wrt_Temperature_Lookup[1]": int.from_bytes(Battery_Capacity_percentage_wrt_Temperature_Lookup[2:4], byteorder='little', signed=False) * 0.01,
		"Battery_Capacity_percentage_wrt_Temperature_Lookup[2]": int.from_bytes(Battery_Capacity_percentage_wrt_Temperature_Lookup[4:6], byteorder='little', signed=False) * 0.01,
		"Battery_Capacity_percentage_wrt_Temperature_Lookup[3]": int.from_bytes(Battery_Capacity_percentage_wrt_Temperature_Lookup[6:8], byteorder='little', signed=False) * 0.01,
		"Battery_Capacity_percentage_wrt_Temperature_Lookup[4]": int.from_bytes(Battery_Capacity_percentage_wrt_Temperature_Lookup[8:10], byteorder='little', signed=False) * 0.01,
		"Battery_Capacity_percentage_wrt_Temperature_Lookup[19]": int.from_bytes(Battery_Capacity_percentage_wrt_Temperature_Lookup[10:12], byteorder='little', signed=False) * 0.01,
		"Battery_Capacity_percentage_wrt_Temperature_Lookup[5]": int.from_bytes(Battery_Capacity_percentage_wrt_Temperature_Lookup[12:14], byteorder='little', signed=False) * 0.01,
		"Battery_Capacity_percentage_wrt_Temperature_Lookup[6]": int.from_bytes(Battery_Capacity_percentage_wrt_Temperature_Lookup[14:16], byteorder='little', signed=False) * 0.01,
		"Battery_Capacity_percentage_wrt_Temperature_Lookup[7]": int.from_bytes(Battery_Capacity_percentage_wrt_Temperature_Lookup[16:18], byteorder='little', signed=False) * 0.01,
		"Battery_Capacity_percentage_wrt_Temperature_Lookup[8]": int.from_bytes(Battery_Capacity_percentage_wrt_Temperature_Lookup[18:20], byteorder='little', signed=False) * 0.01,
		"Battery_Capacity_percentage_wrt_Temperature_Lookup[9]": int.from_bytes(Battery_Capacity_percentage_wrt_Temperature_Lookup[20:22], byteorder='little', signed=False) * 0.01,
		"Battery_Capacity_percentage_wrt_Temperature_Lookup[10]": int.from_bytes(Battery_Capacity_percentage_wrt_Temperature_Lookup[22:24], byteorder='little', signed=False) * 0.01,
		"Battery_Capacity_percentage_wrt_Temperature_Lookup[11]": int.from_bytes(Battery_Capacity_percentage_wrt_Temperature_Lookup[24:26], byteorder='little', signed=False) * 0.01,
		"Battery_Capacity_percentage_wrt_Temperature_Lookup[12]": int.from_bytes(Battery_Capacity_percentage_wrt_Temperature_Lookup[26:28], byteorder='little', signed=False) * 0.01,
		"Battery_Capacity_percentage_wrt_Temperature_Lookup[13]": int.from_bytes(Battery_Capacity_percentage_wrt_Temperature_Lookup[28:30], byteorder='little', signed=False) * 0.01,
		"Battery_Capacity_percentage_wrt_Temperature_Lookup[14]": int.from_bytes(Battery_Capacity_percentage_wrt_Temperature_Lookup[30:32], byteorder='little', signed=False) * 0.01,
		"Battery_Capacity_percentage_wrt_Temperature_Lookup[15]": int.from_bytes(Battery_Capacity_percentage_wrt_Temperature_Lookup[32:34], byteorder='little', signed=False) * 0.01,
		"Battery_Capacity_percentage_wrt_Temperature_Lookup[16]": int.from_bytes(Battery_Capacity_percentage_wrt_Temperature_Lookup[34:36], byteorder='little', signed=False) * 0.01,
		"Battery_Capacity_percentage_wrt_Temperature_Lookup[17]": int.from_bytes(Battery_Capacity_percentage_wrt_Temperature_Lookup[36:38], byteorder='little', signed=False) * 0.01,
		"Battery_Capacity_percentage_wrt_Temperature_Lookup[18]": int.from_bytes(Battery_Capacity_percentage_wrt_Temperature_Lookup[38:40], byteorder='little', signed=False) * 0.01,
		"Battery_Capacity": Battery_Capacity * 0.01,
		"Battery_Usable_Capacity": Battery_Usable_Capacity * 0.01,
		"Cut_off_Battery_positive_High_Temperature": Cut_off_Battery_positive_High_Temperature * 1,
		"Resume_Battery_positive_High_Temperature": Resume_Battery_positive_High_Temperature * 1,
		"Economy_Mode_Maximum_SCU_Temperature": Economy_Mode_Maximum_SCU_Temperature * 1,
		"Limphome_Mode_Maximum_SCU_Temperature": Limphome_Mode_Maximum_SCU_Temperature * 1,
		"Stop_Maximum_SCU_Temperature": Stop_Maximum_SCU_Temperature * 1,
		"Supply_Voltage": Supply_Voltage * 0.01,
		"Duration_for_checking_the_Supply_Voltage": str( int(Duration_for_checking_the_Supply_Voltage[0:1].hex(), 16)) + ":" +  str(int(Duration_for_checking_the_Supply_Voltage[1:2].hex(), 16)) + ":" + str(int(Duration_for_checking_the_Supply_Voltage[2:3].hex(), 16)),
		"Idle_Time_Check_duration": str( int(Idle_Time_Check_duration[0:1].hex(), 16)) + ":" +  str(int(Idle_Time_Check_duration[1:2].hex(), 16)) + ":" + str(int(Idle_Time_Check_duration[2:3].hex(), 16)),
		"Drive_Charge_Data_Transfer_rate": str( int(Drive_Charge_Data_Transfer_rate[0:1].hex(), 16)) + ":" +  str(int(Drive_Charge_Data_Transfer_rate[1:2].hex(), 16)) + ":" + str(int(Drive_Charge_Data_Transfer_rate[2:3].hex(), 16)),
		"Idle_Data_Transfer_rate": str( int(Idle_Data_Transfer_rate[0:1].hex(), 16)) + ":" +  str(int(Idle_Data_Transfer_rate[1:2].hex(), 16)) + ":" + str(int(Idle_Data_Transfer_rate[2:3].hex(), 16)),
		"Topup_Charge_time_interval": str( int(Topup_Charge_time_interval[0:1].hex(), 16)) + ":" +  str(int(Topup_Charge_time_interval[1:2].hex(), 16)) + ":" + str(int(Topup_Charge_time_interval[2:3].hex(), 16)),
		"Correction_Factor": Correction_Factor * 0.1,
		"Correction_Duration": str( int(Correction_Duration[0:1].hex(), 16)) + ":" +  str(int(Correction_Duration[1:2].hex(), 16)) + ":" + str(int(Correction_Duration[2:3].hex(), 16))
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
                        "BPSettings" : self.json
                    }
                }
            
            kafka_manager.kafkaProducer('battorch-to-metrics', msg)
        
        
        #sys.exit(0)
        time.sleep(0.1)
    
if __name__ == '__main__':

    #Test Case begings
    binFile = '/var/tmp/20181127-0018.bp-settingsbin'
    print(binFile)
    p1 = BPSetting()
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

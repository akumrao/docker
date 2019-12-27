//============================================================================
// Name        : CcuUpsController.cpp
// Author      : Arvind Umrao <arvindumrao@yahoo.com>
// Version     :
// Copyright   : Copyright Arvind, Bangalore India
// Description : UPS TRAP listener and Poll SNMP Entries of UPS 
//
//============================================================================

/*
 * I am polling UPS every five mins and reading following UPS Entries.
 * a) upsBatteryStatus",  "Des":"(1-unknown, 2-batteryNormal, 3-batteryLow, 4-batteryDepleted)"
 * b) upsSecondsOnBattery",  "Des":"Seconds elapsed time since the UPS last switched to battery power"
 * c) upsEstimatedMinutesRemaining", "Des":"Battery charge remaining"
 * d) upsEstimatedChargeRemaining", "Des":"Percentage Battery charge remaining"
 * e) upsBatteryVoltage",  "Des":"Magnitude of the present battery voltage."
 * f) upsBatteryTemperature"  "Des":"Temperature at or near the UPS Battery casing

 * Also I am listening to all the alerts as mentioned in config file attached with this  email. And tested following alerts so far.
 * a) Battery Mode
 * b) Line Mode
 * c) Battery Test Mode
 * For provisioning of UPS, we could change default ip from 192.168.102.230 to 192.168.1.113.
 * With following command.
 * curl "http://192.168.102.230/cgi-bin/setSNMPcfg.cgi?name=iptype&?params=0,192.168.1.113,255.255.255.0,192.168.1.254,0.0.0.0&?sid=0.3030867333677893"
 * After default ip change success,  ping 192.168.1.113
 * If ping successful then change the trap ip to
 * curl "http://192.168.1.113/cgi-bin/setSNMPcfg.cgi?name=trapip1&?params=192.168.1.2&?sid=0.25896738550782894"
 * g++ -g CcuUpsController.cpp CcuUpsSnmpGet.cpp CcuUpsSnmpTrap.cpp  -lpthread -lsnmp  -o test9
 * g++ -g CcuUpsController.cpp CcuUpsSnmpGet.cpp CcuUpsSnmpTrap.cpp  ../AppSw/CcuKafkaMessage.cpp  -lsnmp -lpthread -lcppkafka ../OsEncap/libosencap.a -I/ccu/src/OsEncap/ -o test11
 * For Kafka Error logging
 * export SMCCULOGDEBUGS='d'
 * export SMCCULOGERRORS=d
 * export MQISSERIALNUMBER="arvind"
 * Some useful commands
 * net-snmp-config --default-mibdirs
 * mibs +TCP-MIB
 * snmptranslate -Tt | head
 * net-snmp-config --configure-options
 * net-snmp-config --cflags
 * net-snmp-config --libs
 * nc you can listen on an udp port. The magic packet usually is sent to port 9 via broadcast. nc -ul -p 9
 * wakeonlan  54:bf:64:04:07:43
 * ethtool eth0
 * do not use, it does not work tcpdump -i enp1s0 '(udp and port 7) or (udp and port 9)' -x | tee wol.log
 */


#include <iostream>
#include <fstream>
#include <sstream>

#include <unistd.h>

#include <stdio.h>


#include <time.h>
#include <sys/time.h>
#include <vector>

#include "CcuUpsController.h"

#include "rapidjson/document.h"
#include "rapidjson/istreamwrapper.h"
#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"
#include "rapidjson/ostreamwrapper.h"

using namespace std;
using namespace rapidjson;

static CcuUpsController *gUPSCtlrP = NULL;


const char* GET_SNMP_KEY = "UPS-GET-SNMP";
const char* TRAP_SNMP_KEY = "UPS-GET-Trap";


CcuUpsController::CcuUpsController():objSnmpGet(NULL)
{

}

CcuUpsController::~CcuUpsController()
{

    if (objSnmpGet)
        delete objSnmpGet;
    
    if (gUPSCtlrP)
        delete gUPSCtlrP;

}

int
CcuUpsController::Execute()
{
    objSnmpGet->Run();
    objUpsSnmpTrap->Run();

    objSnmpGet->Join();
    objUpsSnmpTrap->Join();
    
    return 0;
}

int CcuUpsController::Init(char* modelFileNameP)
{
    
    if (!modelFileNameP)
    {
        return -1;
    }

    std::ifstream ifs(modelFileNameP);
    if (!ifs.is_open())
    {
        return -1;
    }

    IStreamWrapper isw(ifs);

    Document doc{};
    doc.ParseStream(isw);

    {
        objSnmpGet = new CcuUpsSnmpGet();
        Value& charListMapping = doc[GET_SNMP_KEY];

        int sz = charListMapping.Size();

        for (int i = 0; i < sz; i++)
        {
            typeParam action;
            for (Value::ConstMemberIterator iter = charListMapping[i].MemberBegin(); iter != charListMapping[i].MemberEnd(); ++iter)
            {
                string key = iter->name.GetString();
                
                if( i == 0)
                {
                    if( key == "ip" && iter->value.IsString() )
                    {
                        objSnmpGet->setIP(iter->value.GetString()); 
                    }
                    else if( key == "port" && iter->value.IsString() )
                    {
                        objSnmpGet->setPort( iter->value.GetString()); 
                    }
                    else if( key == "polltime_secs" && iter->value.IsUint() )
                    {
                        objSnmpGet->setPollTime((short) (iter->value.GetUint()));
                    }        
                }
                else
                {
                    if( iter->value.IsString() )
                    {
                        action[key] = iter->value.GetString();
                    }
                }
            }
            if( i > 0)
            {       if( i == 1)
                    objSnmpGet->Init();
                objSnmpGet->addAction(action);
            }
        }
    }

    {
        objUpsSnmpTrap = new CcuUpsSnmpTrap();
        objUpsSnmpTrap->Init();
        Value& charListMapping = doc[TRAP_SNMP_KEY];
        int sz = charListMapping.Size();

        for (int i = 0; i < sz; i++)
        {
            typeParam action;
            for (Value::ConstMemberIterator iter = charListMapping[i].MemberBegin(); iter != charListMapping[i].MemberEnd(); ++iter)
            {
                 string key = iter->name.GetString();
                
                if( i == 0)
                {
                    if( key == "ip" && iter->value.IsString() )
                    {
                        objUpsSnmpTrap->setIP(iter->value.GetString()); 
                    }
                    else if( key == "port" && iter->value.IsString() )
                    {
                        objUpsSnmpTrap->setPort( iter->value.GetString()); 
                    }
                }
                else
                {
                    if( iter->value.IsString() )
                    {
                        action[key] = iter->value.GetString();
                    }
                }
            }
            if( i > 0)
            {   
                objUpsSnmpTrap->addAction(action);
            }
        }
    }
   // cout <<  get_snmp_ip << " " << get_snmp_port << " " << get_snmp_polltime << " " <<   trap_snmp_ip << " " <<  trap_snmp_port  << endl;

    return 0;
}

int main(int argc, char** argv)
{
   // Support for daemon mode
    char* daemonEnvP = NULL;

    if (((daemonEnvP = getenv("SMCCUDMODE")) != NULL) &&
            (!strcmp(daemonEnvP, "daemon")))
    {
        if (daemon(1, 0) == -1)
        { // Do not change working directory and redirect all output to /dev/null
            exit(-1);
        }
    }



    gUPSCtlrP = new CcuUpsController();

    if (gUPSCtlrP->Init((char*) "CcuUpsConfig.json") == -1)
    {
        return -1;
    }else if (gUPSCtlrP->Execute() == -1)
    {
        return -1;
    }

    return 0;
}


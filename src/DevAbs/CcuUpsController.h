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
 */

#ifndef _CCU_UPSCONTROLLER_H_
#define _CCU_UPSCONTROLLER_H_

#include <string>
#include <map>
#include <list>

#include "CcuUpsSnmpTrap.h"
#include "CcuUpsSnmpGet.h"

class CcuUpsController {
public:

    CcuUpsController();
    ~CcuUpsController();

    int Init(char* modelFileNameP);
    int Execute();


protected:

private:
    CcuUpsSnmpGet *objSnmpGet;
    CcuUpsSnmpTrap *objUpsSnmpTrap;
    //std::string get_snmp_ip;
    //std::string trap_snmp_ip;
    //std::string get_snmp_port;
    //std::string trap_snmp_port;
    //int get_snmp_polltime;
};

#endif // _CCU_CAN_WHEELER_CONTROLLER_H_

//============================================================================
// Name        : CcuUpsSnmpTrap.cpp
// Author      : Arvind Umrao <arvindumrao@yahoo.com>
// Version     :
// Copyright   : Copyright Arvind, Bangalore India
// Description : Capture UPS TRAPS
//
//============================================================================

/*
 * CcuUpsSnmpTrap.cpp - Listen TRAPS of UPS at port 162.
 *
 * g++ -g CcuUpsSnmpTrap.cpp ../AppSw/CcuKafkaMessage.cpp  -lsnmp -lpthread -lcppkafka ../OsEncap/libosencap.a -I/ccu/src/OsEncap/ -o test1
 */

#ifndef _CCU_CCcuUpsSnmpTrap_H_
#define _CCU_CCcuUpsSnmpTrap_H_


#include <string>
#include <vector>
#include <utility>
#include <map>
#include <iostream>
#include <thread>
#include <atomic>

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/utilities.h>
#include <net-snmp/net-snmp-includes.h>
#include <net-snmp/library/fd_event_manager.h>


typedef std::vector<std::string> typeArg;
typedef std::map<std::string, std::string > typeParam;
typedef std::pair< typeArg, typeParam > typeAction;
typedef std::vector<typeAction> typeRow;


class CcuUpsSnmpTrap {
public:
    CcuUpsSnmpTrap();
    ~CcuUpsSnmpTrap();
    

    void setPort(std::string port);
    void setIP(std::string ip);

    void addAction(typeParam);

    void addRow(typeAction &);

    void Run();
    void Join();
    static void postToKafka(std::string msg, int err);

    void Init();

private:
    void Execute();

    void snmptrapd_close_sessions(netsnmp_session * sess_list);
    netsnmp_session * snmptrapd_add_session(netsnmp_transport *t);
    static int pre_parse(netsnmp_session * session, netsnmp_transport *transport, void *transport_data, int transport_data_length);
    static int snmp_input(int op, netsnmp_session *session, int reqid, netsnmp_pdu *pdu, void *magic);
    static std::string get_result(struct snmp_pdu *pdu, int & err);

    typeRow row;

    std::string Ip;
    std::string default_port;
    std::thread* m_thread;
    std::atomic<bool> running;
};

#endif // _CCU_CCcuUpsSnmpTrap_H_
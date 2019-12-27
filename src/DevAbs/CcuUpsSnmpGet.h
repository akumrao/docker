//============================================================================
// Name        : CcuUpsSnmpGet.cpp
// Author      : Arvind Umrao <arvindumrao@yahoo.com>
// Version     :
// Copyright   : Copyright Arvind, Bangalore India
// Description : Monitor UPS
//
//============================================================================

/*
 * CcuUpsSnmpGet.cpp - Send GET requests to a network entity and retrieve UPS properties.
 *
 * SNMP application that uses the SNMP GET request to query for information on a network entity. 
 * One or more object identifiers (OIDs) may be given as arguments to parse SNMP Request. 
 * g++ -g CcuUpsSnmpGet.cpp ../AppSw/CcuKafkaMessage.cpp  -lsnmp -lpthread -lcppkafka ../OsEncap/libosencap.a -I/ccu/src/OsEncap/ -o test1
 */

#ifndef _CCU_CCcuUpsSnmpGet_H_
#define _CCU_CCcuUpsSnmpGet_H_


#include <string>
#include <vector>
#include <utility>
#include <map>
#include <iostream>
#include <thread>
#include <atomic>

typedef std::vector<std::string> typeArg;
typedef std::map<std::string, std::string > typeParam;
typedef std::pair< typeArg, typeParam > typeAction;
typedef std::vector<typeAction> typeRow;

enum kafka_msg_type{NORMAL,ERR,ALERT };

class CcuUpsSnmpGet {
public:
    CcuUpsSnmpGet();

    void setPollTime(int poll);
    void setPort(std::string port);
    void setIP(std::string ip);
    void Init();
    
    ~CcuUpsSnmpGet();

    void addAction(typeParam);

    void addRow(typeAction &);

    void Run();
    void Join();
    void postToKafka(std::string msg, kafka_msg_type type);

    int parse(int argc, char **argv, int &ret, char *buf);

private:
    void Execute( );
    
    typeArg commonArg;
    typeRow row;

    int polltime;
    std::string Ip;
    std::string Port;
    
    std::thread* m_thread;
    std::atomic<bool> running;
};

#endif // _CCU_CCcuUpsSnmpGet_H_
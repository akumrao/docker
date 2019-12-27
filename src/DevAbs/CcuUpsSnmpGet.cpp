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
 * g++ -g CcuUpsSnmpGet.cpp ../AppSw/CcuKafkaMessage.cpp  -lsnmp -lpthread -lcppkafka ../OsEncap/libosencap.a -I/ccu/src/OsEncap/ -DUNIT_TEST -o test1
 * g++ -g CcuUpsSnmpGet.cpp   -lpthread -lsnmp -DUNIT_TEST -o test1
* curl "http://192.168.102.230/cgi-bin/setSNMPcfg.cgi?name=iptype&?params=0,192.168.1.113,255.255.255.0,192.168.1.254,0.0.0.0&?sid=0.3030867333677893"

* After default ip change success,  ping 192.168.1.113

* If ping successful then change the trap ip to

* curl "http://192.168.1.113/cgi-bin/setSNMPcfg.cgi?name=trapip1&?params=192.168.1.2&?sid=0.25896738550782894"

* wakeup configularion

* curl "http://192.168.1.113/cgi-bin/config.cgi?name=wakeUp&?params=1_54-bf-64-04-07-43&?sid=0.380574749368896"

 * curl "http://192.168.1.113/cgi-bin/config.cgi?name=wakeUp&?params=1_54-bf-64-04-07-43&?sid=0.380574749368896"

 * curl "http://192.168.1.113/cgi-bin/rtControl.cgi?name=needwake&?params=1&?sid=0.48989414697570255"
 * curl "http://192.168.1.113/cgi-bin/rtControl.cgi?name=UPSOnOff&?params=On&?sid=0.9800406612897374"
 * 
 */


#include <net-snmp/net-snmp-config.h>
#include <net-snmp/utilities.h>
#include <net-snmp/net-snmp-includes.h>

#define NETSNMP_DS_APP_DONT_FIX_PDUS 0

#include <algorithm>
#include <chrono>
#include "CcuUpsSnmpGet.h"

#define _KAFKA_ 1
//#define UNIT_TEST 1

#ifdef _KAFKA_

#include <cppkafka/producer.h>
#include "CcuCanWheeler.h"
#include "../AppSw/CcuKafkaMessage.h"
using namespace cppkafka;

#endif //_KAFKA_


CcuUpsSnmpGet::CcuUpsSnmpGet() :  m_thread(NULL),running(true)
{
    
}
void CcuUpsSnmpGet::setPollTime(int poll)
{
    polltime = poll;
    
}
        
void CcuUpsSnmpGet::setPort(std::string port)
{
    Port = port;
}

void CcuUpsSnmpGet::setIP(std::string ip)
{
    Ip = ip;
}

void CcuUpsSnmpGet::Init()
{
    commonArg = {"snmpget", "-c", "public", "-v", "2c", Ip + ":" + Port};
    
    std::string curlcmd = "curl --max-time 10 \"http://192.168.1.113/cgi-bin/rtControl.cgi?name=UPSOnOff&?params=On&?sid=0.9800406612897374\"";
    int ret= system(curlcmd.c_str());
    if( ret <= 0)
        std::cout << "Error in curl command for UPS set " << std::endl;
    
}


CcuUpsSnmpGet::~CcuUpsSnmpGet()
{   
    running = false;
    Join();
}

void CcuUpsSnmpGet::Run()
{
    if (!m_thread)
        m_thread = new std::thread(&CcuUpsSnmpGet::Execute, this);

    return;
}

void CcuUpsSnmpGet::Join()
{
    if (!m_thread)
    return;
    
    m_thread->join();

    delete m_thread;
    m_thread = NULL;

    return;
}

void CcuUpsSnmpGet::Execute()
{
    std::map<std::string, int> storage;

    while (running)
    {

        std::string kafkaMsg;

        typeRow::iterator itr;
        // Displaying vector elements using begin() and end() 
        std::cout << "About to read the UPS parameters." << std::endl;
        for (itr = row.begin(); itr < row.end(); itr++)
        {

            int sz1 = itr->first.size();
            char *tmp[250];
            int i = 0;
            typeArg::iterator ptr;
            for (ptr = itr->first.begin(); ptr < itr->first.end(); ptr++)
            {
                //std::cout<< *ptr <<  std::endl;
                tmp[i] = new char[ptr->length() + 1];
                strncpy(tmp[i], ptr->c_str(), ptr->length());

                tmp[i][ptr->length()] = '\0';

                //std::cout<< tmp[i] <<  std::endl;
                ++i;
            }

            int iret = 0;

            char buf[256] = {'\0'};
            int result = parse(sz1, tmp, iret, buf);
            std::string sbuf = buf;

            i = 0;
            for (ptr = itr->first.begin(); ptr < itr->first.end(); ptr++)
            {
                delete [] tmp[i];
                ++i;
            }

            if (result < 0)
            {
                std::replace_if(sbuf.begin(), sbuf.end(), ::ispunct, '.');
                postToKafka(itr->second["name"] + " " + sbuf, ERR);
            }
            else
            {
                std::replace_if(sbuf.begin(), sbuf.end(), ::ispunct, ' ');
                sbuf = "\"" + sbuf + "\"";
                if (kafkaMsg.length())
                    kafkaMsg = kafkaMsg + ", ";
                kafkaMsg = kafkaMsg + "\"" + itr->second["name"] + "\":" + sbuf;

                storage[itr->second["name"]] = iret;


                if (itr->second["action"] == "None")
                {
                    continue;
                } else if (itr->second.find("action") != itr->second.end() && std::stoi(itr->second["iflesser"]) >= iret)
                {
                    /////
                    bool condCheck = true;
                    if (itr->second.find("and") != itr->second.end())
                    {
                        if (storage.find(itr->second["and"]) != storage.end())
                        {
                            if (storage[itr->second["and"]] == std::stoi(itr->second["equal"]))
                            {
                                condCheck = true;
                                std::cout << "condtion matched" << std::endl;
                            } else
                            {
                                condCheck = false;
                                std::cout << "condtion not matched" << std::endl;
                            }
                        }
                    }

                    if (condCheck)
                    {
                        std::cout << "\"Alert\":\"" + itr->second["des"] + "\"" << std::endl;

                        postToKafka("\"Alert\":\"" + itr->second["des"] + "\"", ALERT);

                        if (itr->second["action"] != "Alert")
                        {
                            int ret = system(itr->second["action"].c_str());
                            if (ret <= 0)
                                std::cout << "Error in executing script" << std::endl;
                        }
                        continue;
                    }
                }
            }
        }

        if (kafkaMsg.length())
            postToKafka(kafkaMsg, NORMAL);

        std::this_thread::sleep_for(std::chrono::seconds(polltime));

    }
}

void CcuUpsSnmpGet::postToKafka(std::string msg, kafka_msg_type type)
{
    std::cout << "err " << type << " msg " << msg <<  std::endl;
    #ifdef _KAFKA_
    

    Configuration kfProducerConfig = {
        { "metadata.broker.list", "127.0.0.1:9092" },
        { "queue.buffering.max.ms", 1 },
        { "group.id", "GROUPUPS" },
		{ "batch.num.messages", 1 }
    };
     
    try
    {
                    // Create the kafka producer
    Producer kfProducer(kfProducerConfig);

    std::string kfKey = CcuKafkaMessage::createKfMsgKey();
    std::string txIdKey = CcuKafkaMessage::createTxIdKey();
                         
    if( type == ERR)
    {
        //std::cout << "CcuUpsSnmpGet " << type << " msg " << msg <<  std::endl;
        CcuKafkaMessage::sendLogMessage(kfProducer, txIdKey, "CcuUpsSnmpGet", "ups", "error",  msg , "{}");
    }                            
    else
    {
        std::string jsonOutput;

        jsonOutput = "{\"mediadoc-time\":" + kfKey + ",";
        jsonOutput += "\"mediadoc-txIdKey\":\"" + txIdKey + "\",";
        jsonOutput += "\"mediadoc-source\":{\"type\":\"UPS\"},";
        jsonOutput += "\"mediadoc-recordType\":\"UPS-MONITOR-DATA\",\"mediadoc-data\":{\"UPSmetrics\":{";
        jsonOutput += msg;
        jsonOutput += "}}}";

        if(type == NORMAL)
        {
            MessageBuilder kfMessageBuilder = MessageBuilder ("upsorch-to-metrics");
            kfMessageBuilder.partition(0).key(kfKey).payload(jsonOutput);

            kfProducer.produce(kfMessageBuilder);
        }
        else
            CcuKafkaMessage::sendAlert (kfProducer, txIdKey, "ups-battery-critical", "CcuUpsSnmpGet", true, "CcuUpsSnmpGet", jsonOutput);
    }
    
    std::chrono::milliseconds flushTmo (60000);
    kfProducer.flush(flushTmo);
    //kfProducer.flush();
    }
    catch(...)
    {
        
    }

                    // Dispatch a SECU
    #endif //_KAFKA_
}

void CcuUpsSnmpGet::addAction(typeParam param)
{
    typeAction type;

    type.first = commonArg;
    type.first.push_back(param["oid"]);
    type.second = param;

    addRow(type);
}

void CcuUpsSnmpGet::addRow(typeAction &action)
{
    row.push_back(action);
}

int CcuUpsSnmpGet::parse(int argc, char **argv, int &ret, char *buf)
{
    netsnmp_session session, *ss;
    netsnmp_pdu *pdu;
    netsnmp_pdu *response = NULL;
    netsnmp_variable_list *vars;
    int arg;
    int count;
    int current_name = 0;
    char *names[SNMP_MAX_CMDLINE_OIDS];
    oid name[MAX_OID_LEN];
    size_t name_length;
    int status;
    int failures = 0;
    int exitval = 0;

    /*
     * get the common command line arguments 
     */
    switch (arg = snmp_parse_args(argc, argv, &session, NULL, NULL))
    {
        case -2:
            sprintf(buf, "%s", "In valid SNMP Get parameters.");
            return -2;
        case -1:
            sprintf(buf, "%s", "In valid SNMP Get parameters.");
            return -1;
        default:
            break;
    }

    if (arg >= argc)
    {
        fprintf(stderr, "Missing object name\n");
        sprintf(buf, "%s", "Missing object name");

        return -3;
    }
    if ((argc - arg) > SNMP_MAX_CMDLINE_OIDS)
    {
        fprintf(stderr, "Too many object identifiers specified. ");
        fprintf(stderr, "Only %d allowed in one request.\n", SNMP_MAX_CMDLINE_OIDS);
        sprintf(buf, "Only %d allowed in one request.", SNMP_MAX_CMDLINE_OIDS);
        return -3;
    }

    /*
     * get the object names 
     */
    for (; arg < argc; arg++)
        names[current_name++] = argv[arg];

    try
    {

        SOCK_STARTUP;


        /*
         * Open an SNMP session.
         */
        ss = snmp_open(&session);
        if (ss == NULL)
        {
            /*
             * diagnose snmp_open errors with the input netsnmp_session pointer 
             */
            snmp_sess_perror("snmpget", &session);
            SOCK_CLEANUP;

            sprintf(buf, "%s", "Netsnmp_session error.");
            return -3;

        }

        /*
         * Create PDU for GET request and add object names to request.
         */
        pdu = snmp_pdu_create(SNMP_MSG_GET);
        for (count = 0; count < current_name; count++)
        {
            name_length = MAX_OID_LEN;
            if (!snmp_parse_oid(names[count], name, &name_length))
            {
                snmp_perror(names[count]);
                failures++;
            } else
                snmp_add_null_var(pdu, name, name_length);
        }
        if (failures)
        {
            snmp_close(ss);
            SOCK_CLEANUP;
            sprintf(buf, "%s", "Error during SNMP Get");
            exitval = -5;
        }

        /*
         * Perform the request.
         *
         * If the Get Request fails, note the OID that caused the error,
         * "fix" the PDU (removing the error-prone OID) and retry.
         */
retry:
        status = snmp_synch_response(ss, pdu, &response);
        if (response && status == STAT_SUCCESS )
        {
            if (response->errstat == SNMP_ERR_NOERROR)
            {
                for (vars = response->variables; vars;
                        vars = vars->next_variable)
                {

                    if (vars->type == ASN_INTEGER)
                    {
                        ret = *vars->val.integer;
                        sprintf(buf, "%d", (int) *vars->val.integer);
                    } else if (vars->type == ASN_OCTET_STR)
                    {
                        sprintf(buf, "\"%s\"", vars->val.string);
                    } else
                    {
                        fprint_objid(stderr, vars->name, vars->name_length);
                        snprint_variable(buf, 256, vars->name, vars->name_length, vars);
                        exitval = -6;
                    }
                }

            } else
            {
                fprintf(stderr, "Error in packet\nReason: %s\n",
                        snmp_errstring(response->errstat));

                if (response->errindex != 0)
                {
                    fprintf(stderr, "Failed object: ");
                    for (count = 1, vars = response->variables;
                            vars && count != response->errindex;
                            vars = vars->next_variable, count++)
                        /*EMPTY*/;
                    if (vars)
                    {
                        fprint_objid(stderr, vars->name, vars->name_length);
                        snprint_variable(buf, 256, vars->name, vars->name_length, vars);

                    }
                    fprintf(stderr, "\n");
                }
                exitval = -6;

                /*
                 * retry if the errored variable was successfully removed 
                 */
                if (!netsnmp_ds_get_boolean(NETSNMP_DS_APPLICATION_ID,
                        NETSNMP_DS_APP_DONT_FIX_PDUS))
                {
                    pdu = snmp_fix_pdu(response, SNMP_MSG_GET);
                    snmp_free_pdu(response);
                    response = NULL;
                    if (pdu != NULL)
                    {
                        goto retry;
                    }
                }
            } /* endif -- SNMP_ERR_NOERROR */

        } else if (status == STAT_TIMEOUT)
        {
            fprintf(stderr, "Timeout: No Response from %s.\n", session.peername);
            sprintf(buf, "Timeout, No Response from %s", session.peername);
            exitval = -4;

        } else
        { /* status == STAT_ERROR */
            snmp_sess_perror("snmpget", ss);
            sprintf(buf, "%s", "Error during SNMP Get");
            exitval = -5;

        } /* endif -- STAT_SUCCESS */

        if (response)
            snmp_free_pdu(response);
        snmp_close(ss);
        SOCK_CLEANUP;

    }    catch (...)
    {
        exitval = -4;
    }

    return exitval;

} /* end main() */

#ifdef UNIT_TEST
int
main(int argc, char *argv[])
{
    CcuUpsSnmpGet *objSnmpGet = new CcuUpsSnmpGet();

    objSnmpGet->setPollTime(6);
    objSnmpGet->setPort("161");
    objSnmpGet->setIP("localhost");
    objSnmpGet->Init();
    
    typeParam action;

    action["action"] = "None";
    action["name"] = "OS";
    action["oid"] = "iso.3.6.1.2.1.1.7.0";
    objSnmpGet->addAction(action);

    
    action["action"] = "./mediadoc-runcmd-on-host1.sh";
    action["name"] = "Uptime";
    action["oid"] = "iso.3.6.1.2.1.1.7.0";
    action["iflesser"] = "72";
    action["and"] = "OS";
    action["equal"] = "72";
    action["des"] = "script";
    objSnmpGet->addAction(action);
    
    action["action"] = "Alert";
    action["name"] = "Uptime";
    action["oid"] = "iso.3.6.1.2.1.1.7.0";
    action["iflesser"] = "72";
    action["and"] = "OS";
    action["des"] = "Alert msg";
    
    objSnmpGet->addAction(action);
    
    objSnmpGet->Run();

    std::this_thread::sleep_for(std::chrono::seconds(5000));

    delete objSnmpGet;

}

#endif //UNIT_TEST
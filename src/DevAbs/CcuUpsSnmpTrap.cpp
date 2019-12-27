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
 * g++ -g CcuUpsSnmpTrap.cpp ../AppSw/CcuKafkaMessage.cpp  -lsnmp -lpthread -lcppkafka ../OsEncap/libosencap.a -I/ccu/src/OsEncap/ -o test5
 * With following command.

* curl "http://192.168.102.230/cgi-bin/setSNMPcfg.cgi?name=iptype&?params=0,192.168.1.113,255.255.255.0,192.168.1.254,0.0.0.0&?sid=0.3030867333677893"

* After default ip change success,  ping 192.168.1.113

* If ping successful then change the trap ip to

* curl "http://192.168.1.113/cgi-bin/setSNMPcfg.cgi?name=trapip1&?params=192.168.1.2&?sid=0.25896738550782894"

* wakeup configularion

* curl "http://192.168.1.113/cgi-bin/config.cgi?name=wakeUp&?params=1_54-bf-64-04-07-43&?sid=0.380574749368896"

 * curl "http://192.168.1.113/cgi-bin/config.cgi?name=wakeUp&?params=1_54-bf-64-04-07-43&?sid=0.380574749368896"

 * curl "http://192.168.1.113/cgi-bin/rtControl.cgi?name=needwake&?params=1&?sid=0.48989414697570255"
 * 
 */



#define NETSNMP_DS_APP_DONT_FIX_PDUS 0


#include <chrono>
#include "CcuUpsSnmpTrap.h"

#include <errno.h>
#include <algorithm>

#define _KAFKA_ 1
//#define UNIT_TEST 1

#ifdef _KAFKA_

#include <cppkafka/producer.h>
#include "CcuCanWheeler.h"
#include "../AppSw/CcuKafkaMessage.h"
using namespace cppkafka;

#endif //_KAFKA_


CcuUpsSnmpTrap::CcuUpsSnmpTrap() : m_thread(NULL), running(true)
{
    default_port = "udp:162";
}

void CcuUpsSnmpTrap::setPort(std::string port)
{
    default_port = port;
}

void CcuUpsSnmpTrap::setIP(std::string ip)
{
    Ip = ip;
}

CcuUpsSnmpTrap::~CcuUpsSnmpTrap()
{
    running = false;
    Join();
}

void CcuUpsSnmpTrap::Init()
{
    SOCK_STARTUP;
    /* initialize library */
    init_snmp("snmptrapd");
}

std::string CcuUpsSnmpTrap::get_result(struct snmp_pdu *pdu, int & err)
{
    char buf[1024];
    struct variable_list *vars;
    std::string ret;

    if (pdu->errstat == SNMP_ERR_NOERROR)
    {
        for (vars = pdu->variables; vars;
                vars = vars->next_variable)
        {

            if (vars->type == ASN_INTEGER)
            {
                fprint_objid(stderr, vars->name, vars->name_length);
                //ret = *vars->val.integer;
                //sprintf(buf, "%d", *vars->val.integer);
                fprintf(stderr, "value = %d\n", (int)*vars->val.integer);
                //ret += buf;
            } else if (vars->type == ASN_OCTET_STR)
            {
                fprintf(stderr, "value=%s\n", vars->val.string);
                sprintf(buf, "%s", vars->val.string);
                ret += buf;
            } else
            {
                fprint_objid(stderr, vars->name, vars->name_length);
                //fprintf(stderr, "value is NOT a valid type\n");
                //snprint_variable(buf, sizeof (buf), vars->name, vars->name_length, vars);
                //ret += buf;
                //err = -6;
            }
        }


    } else
    {
        int count = 0;
        for (count = 1, vars = pdu->variables;
                vars && count != pdu->errindex;
                vars = vars->next_variable, count++)
            /*EMPTY*/;
        if (vars)
        {
            fprint_objid(stderr, vars->name, vars->name_length);
            snprint_variable(buf, sizeof (buf), vars->name, vars->name_length, vars);

        }
        err = -6;
        ret += buf + std::string(" ,") + std::string(snmp_errstring(pdu->errstat));
    }


    return ret;
}

int CcuUpsSnmpTrap::snmp_input(int op, netsnmp_session *session, int reqid, netsnmp_pdu *pdu, void *magic)
{
    std::string msg;
    int err = 0;
    switch (op)
    {
        case NETSNMP_CALLBACK_OP_RECEIVED_MESSAGE:
            /*
             * Drops packets with reception problems
             */
            if (session->s_snmp_errno)
            {
                /* drop problem packets */
                msg = "Packet drop problem.";
                err = -1;
                break;
            }

            /*
             * Determine the OID that identifies the trap being handled
             */
            DEBUGMSGTL(("snmptrapd", "input: %x\n", pdu->command));
            switch (pdu->command)
            {
                case SNMP_MSG_TRAP:
                    /*
                     * Convert v1 traps into a v2-style trap OID
                     *    (following RFC 2576)
                     */
                    msg = get_result(pdu, err);
                    break;

                case SNMP_MSG_TRAP2:
                case SNMP_MSG_INFORM:
                    msg = get_result(pdu, err);
                    break;

                default:
                    /* SHOULDN'T HAPPEN! */
                    msg = "SHOULDN'T HAPPEN!";
                    err = -2;
                    break;
            }

            break;

        case NETSNMP_CALLBACK_OP_TIMED_OUT:
            snmp_log(LOG_ERR, "Timeout: This shouldn't happen!\n");
            msg = "Timeout. This shouldn't happen!";
            err = -3;
            break;

        case NETSNMP_CALLBACK_OP_SEND_FAILED:
            snmp_log(LOG_ERR, "Send Failed: This shouldn't happen either!\n");
            msg = "Send Failed.This shouldn't happen either!";
            err = -3;
            break;

        case NETSNMP_CALLBACK_OP_CONNECT:
        case NETSNMP_CALLBACK_OP_DISCONNECT:
            /* Ignore silently */
            break;

        default:
            snmp_log(LOG_ERR, "Unknown operation (%d): This shouldn't happen!\n", op);
            msg = "Unknown operation. This shouldn't happen!";
            err = -3;
            break;
    }

    postToKafka(msg, err);
    return 0;
}

int CcuUpsSnmpTrap::pre_parse(netsnmp_session * session, netsnmp_transport *transport, void *transport_data, int transport_data_length)
{
    return 1;
}

netsnmp_session * CcuUpsSnmpTrap::snmptrapd_add_session(netsnmp_transport *t)
{
    netsnmp_session sess, *session = &sess, *rc = NULL;

    snmp_sess_init(session);
    session->peername = SNMP_DEFAULT_PEERNAME; /* Original code had NULL here */
    session->version = SNMP_DEFAULT_VERSION;
    session->community_len = SNMP_DEFAULT_COMMUNITY_LEN;
    session->retries = SNMP_DEFAULT_RETRIES;
    session->timeout = SNMP_DEFAULT_TIMEOUT;
    session->callback = snmp_input;
    session->callback_magic = (void *) t;
    session->authenticator = NULL;
    sess.isAuthoritative = SNMP_SESS_UNKNOWNAUTH;

    rc = snmp_add(session, t, pre_parse, NULL);
    if (rc == NULL)
    {
        snmp_sess_perror("snmptrapd", session);
    }
    return rc;
}

void CcuUpsSnmpTrap::snmptrapd_close_sessions(netsnmp_session * sess_list)
{
    netsnmp_session *s = NULL, *next = NULL;

    for (s = sess_list; s != NULL; s = next)
    {
        next = s->next;
        snmp_close(s);
    }
}

void CcuUpsSnmpTrap::Run()
{
    if (!m_thread)
        m_thread = new std::thread(&CcuUpsSnmpTrap::Execute, this);

    return;
}

void CcuUpsSnmpTrap::Join()
{
    if (!m_thread)
        return;
    
    
    m_thread->join();

    delete m_thread;
    m_thread = NULL;

    return;
}

void CcuUpsSnmpTrap::Execute()
{

    netsnmp_session *sess_list = NULL, *ss = NULL;
    netsnmp_transport *transport = NULL;
    transport = netsnmp_transport_open_server("snmptrap", default_port.c_str());
    if (transport == NULL)
    {
        snmp_log(LOG_ERR, "couldn't open %s -- errno %d (\"%s\")\n",
                default_port.c_str(), errno, strerror(errno));
        snmptrapd_close_sessions(sess_list);
        SOCK_CLEANUP;
        exit(1);
    } else
    {
        ss = snmptrapd_add_session(transport);
        if (ss == NULL)
        {
            /*
             * Shouldn't happen?  We have already opened the transport
             * successfully so what could have gone wrong?  
             */
            snmptrapd_close_sessions(sess_list);
            netsnmp_transport_free(transport);
            snmp_log(LOG_ERR, "couldn't open snmp - %s", strerror(errno));
            SOCK_CLEANUP;
            exit(1);
        } else
        {
            ss->next = sess_list;
            sess_list = ss;
        }
    }



    int count, numfds, block;
    fd_set readfds, writefds, exceptfds;
    struct timeval timeout, *tvp;


    netsnmp_logging_restart();
    snmp_log(LOG_INFO, "NET-SNMP version %s restarted\n",
            netsnmp_get_version());

    while (running)
    {

        numfds = 0;
        FD_ZERO(&readfds);
        FD_ZERO(&writefds);
        FD_ZERO(&exceptfds);
        block = 0;
        tvp = &timeout;
        timerclear(tvp);
        tvp->tv_sec = 5;
        snmp_select_info(&numfds, &readfds, tvp, &block);
        if (block == 1)
            tvp = NULL; /* block without timeout */
        netsnmp_external_event_info(&numfds, &readfds, &writefds, &exceptfds);
        count = select(numfds, &readfds, &writefds, &exceptfds, tvp);
        //gettimeofday(&Now, 0);
        if (count > 0)
        {
            netsnmp_dispatch_external_events(&count, &readfds, &writefds,
                    &exceptfds);
            /* If there are any more events after external events, then
             * try SNMP events. */
            if (count > 0)
            {
                snmp_read(&readfds);
            }
        } else
            switch (count)
            {
                case 0:
                    snmp_timeout();
                    continue;
                case -1:
                    if (errno == EINTR)
                        continue;
                    snmp_log_perror("select");
                    running = false;
                    break;
                default:
                    fprintf(stderr, "select returned %d\n", count);
                    snmp_log_perror("select returned");
                    running = false;
            }
        run_alarms();
    }


}

void CcuUpsSnmpTrap::postToKafka(std::string msg, int err)
{

    std::cout << "err " << err << " msg " << msg <<  std::endl;

    if( !msg.length())
        return; 
            
#ifdef _KAFKA_

    Configuration kfProducerConfig = {
        { "metadata.broker.list", "127.0.0.1:9092"},
        { "queue.buffering.max.ms", 1},
        { "group.id", "GROUPUPS"},
        { "batch.num.messages", 1}
    };


    // Create the kafka producer
    Producer kfProducer(kfProducerConfig);

    std::string kfKey = CcuKafkaMessage::createKfMsgKey();
    std::string txIdKey = CcuKafkaMessage::createTxIdKey();

    std::replace_if(msg.begin(), msg.end(), ::ispunct, '.');

    if (err)
    {
        //string textLogMessage = msg
        CcuKafkaMessage::sendLogMessage(kfProducer, txIdKey, "CcuUpsSnmpTrap", "ups", "error", msg, "{}");
    } else
    {
        std::replace_if(msg.begin(), msg.end(), ::ispunct, ' ');
        msg = "\"" + msg + "\"";

        msg = "\"Trap\":" + msg;

        std::string jsonOutput;

        jsonOutput = "{\"mediadoc-time\":" + kfKey + ",";
        jsonOutput += "\"mediadoc-txIdKey\":\"" + txIdKey + "\",";
        jsonOutput += "\"mediadoc-source\":{\"type\":\"UPS\"},";
        jsonOutput += "\"mediadoc-recordType\":\"UPS-TRAPS\",\"mediadoc-data\":{\"UPSmetrics\":{";
        jsonOutput += msg;
        jsonOutput += "}}}";

        //std::cout << "err " << "about send kafka" << " msg " << msg <<  std::endl;
        
        CcuKafkaMessage::sendAlert (kfProducer, txIdKey, "ups-trap", "CcuUpsSnmpTrap", false, "CcuUpsSnmpTrap", jsonOutput);
        
        //MessageBuilder kfMessageBuilder = MessageBuilder("upsorch-to-metrics");
        //kfMessageBuilder.partition(0).key(kfKey).payload(jsonOutput);

        //kfProducer.produce(kfMessageBuilder);
    }
    std::chrono::milliseconds flushTmo (60000);
    kfProducer.flush(flushTmo);
    //kfProducer.flush();

    // Dispatch a SECU
#endif //_KAFKA_
}

void CcuUpsSnmpTrap::addAction(typeParam action)
{
    typeAction type;

    // type.first = commonArg;
    type.first.push_back(action["name"]);

    type.second = action;

    addRow(type);
}

void CcuUpsSnmpTrap::addRow(typeAction &action)
{
    row.push_back(action);
}


#ifdef UNIT_TEST

int
main(int argc, char *argv[])
{

    std::string str = "example\"':string\n";

    std::replace_if(str.begin(), str.end(), ::ispunct, ' ');

    std::cout << str << std::endl;

    CcuUpsSnmpTrap *objUpsSnmpTrap = new CcuUpsSnmpTrap();

    typeParam action;

    action["action"] = "NONE";
    action["name"] = "Uptime";

    objUpsSnmpTrap->addAction(action);

    action["action"] = "NONE";
    action["name"] = "OS";

    objUpsSnmpTrap->addAction(action);

    objUpsSnmpTrap->Init();
    objUpsSnmpTrap->Run();

    std::this_thread::sleep_for(std::chrono::seconds(5000));

    delete objUpsSnmpTrap;
}

#endif //UNIT_TEST
#!/bin/bash
#
set -ex
#
export SMCCUSWAPMODE="norf"
#export SMCCUSIMMODE="-sim"

export LOGFILE_PREFIX="/ccu/log/$(date '+%Y%m%d%H%M%S')"
export MODE="production"
#export MODE="debug" 
#
export SMCCUENABLETHERMALRULES=1

#
export SMCCULOGERRORS=1
export SMCCULOGDEBUGS=1
#

#
# Setting Station Serial as env variable
mqisName=`cat /ccu/setup/config.yaml| grep serial_number | awk '{print $2}'| head -1`
if [ "$mqisName" == "WMQISXM1V1-0000x" ]
then
        mqisName=`hostname`
fi
export MQISSERIALNUMBER=$mqisName
#
# Start SmartCard/RFID Driver
#/etc/init.d/pcscd restart
#
# Start Zookeeper & Kafka
/etc/init.d/zookeeper restart
export KAFKA_OPTS="-Djava.net.preferIPv4Stack=True"
cd /kafka_2.11-1.1.0 && bin/kafka-server-start.sh -daemon config/server.properties
#
# Start ElasticSearch and Kibana
/etc/init.d/kibana restart
cp -fp /ccu/src/config/media-doc-ES-jvm.options /etc/elasticsearch/jvm.options
cp -fp /ccu/src/config/media-doc-ES-elasticsearch.yml /etc/elasticsearch/elasticsearch.yml
/etc/init.d/elasticsearch restart
#
# Start logstash pipeline from Kafka to ElasticSearch
cp -fp /ccu/src/config/media-doc-Logstash.conf /etc/logstash/conf.d/media-doc-Logstash.conf
nohup /usr/share/logstash/bin/logstash -f /etc/logstash/conf.d/media-doc-Logstash.conf -r --config.reload.automatic &
sleep 5
#
echo "Waiting 60 secs for ElasticSearch, Kibana, Logstash, Zookeeper and Kafka service initialization ...."
sleep 60
#
# Initialization of CCU ElasticSearch DB
echo ""
echo "Initializing CCU DB ...."
cd /ccu/src/DevAbs
./mediadoc-dynamic-db-init.sh $SMCCUINITBPDOCKDB $SMCCUINITCLOUDDB
echo ""
#

#!/bin/bash
#
set -ex
#
export SMCCUSWAPMODE="norf"
#export SMCCUSIMMODE="-sim"
#export SMCCUINITBPDOCKDB="initbpdockdb"
#export SMCCUINITCLOUDDB="initclouddb"
export LOGFILE_PREFIX="/ccu/log/$(date '+%Y%m%d%H%M%S')"
export MODE="production"
#export MODE="debug" 
#
export SMCCUENABLETHERMALRULES=1
#export SMCCURESETCHARGERONFAULTS=1
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
/etc/init.d/pcscd restart
#
# Start Zookeeper & Kafka
/etc/init.d/zookeeper restart
export KAFKA_OPTS="-Djava.net.preferIPv4Stack=True"
if [ -d /kafka ]
then
	cd /kafka && bin/kafka-server-start.sh -daemon config/server.properties
else
#	Stopgap till /kafka softlink is created during the next Docker build to remove version specific directories inside the CCU scripts
	if [ -d /kafka_2.11-1.1.0 ]
	then
		cd /kafka_2.11-1.1.0 && bin/kafka-server-start.sh -daemon config/server.properties
	fi
	if [ -d /kafka_2.11-1.1.1 ]
	then
		cd /kafka_2.11-1.1.1 && bin/kafka-server-start.sh -daemon config/server.properties
	fi
fi	
#
# Start ElasticSearch and Kibana
/etc/init.d/kibana restart
cp -fp /ccu/src/config/media-doc-ES-jvm.options /etc/elasticsearch/jvm.options
cp -fp /ccu/src/config/media-doc-ES-elasticsearch.yml /etc/elasticsearch/elasticsearch.yml
ulimit -l unlimited
ulimit -n 65536
ulimit -u 4096
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
cd /ccu/src/DevAbs
#
if [ "$SMCCUSIMMODE" == "-sim" ]
then
	echo "Bypassing GPIO controls in simulation mode ...."
else
	echo ""
	echo "!!!IMPORTANT!!! Turning Off Dock  ...."
# PLC IP Addresses and bitmaps are hardcoded for XM1, XM2 and XM3
	#./clidirect 192.168.1.177 -wr 0
	echo ""
#
	echo ""

	echo ""
fi
#
# Install ccuUI and associated python requirement with cacheing
cd /
#export PYDIST_TGZ="/ccu/py36-dist-packages.tgz"
#if ! tar xvzf "${PYDIST_TGZ}"; then
#    pip3 install -r /ccu/ccuUI/requirements.txt
#    tar cvzf "${PYDIST_TGZ}" usr/local/lib/python3.6/dist-packages/
#fi
#cd /ccu/ccuUI/www/src && coffee -bmc *.coffee
#
sleep 5
#
# Start all CCU application services
cd /ccu/src
screen -Logfile ${LOGFILE_PREFIX}-screen.log -c screenrc
while sleep 1; do
	screen -ls
	/bin/bash
done

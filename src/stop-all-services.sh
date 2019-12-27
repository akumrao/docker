#!/bin/bash
#
set -x
#
#export SMCCUSIMMODE="-sim"
ENTRY_POINT="/ccu/src/stop-all-services.sh"
#
if [ -d /docker/src/DevAbs ]
then
#	Stopping all the services
#	Stop RFID service
	/etc/init.d/pcscd stop
# 	Stop Kafka
	if [ -d /kafka ]
	then
		/kafka/bin/kafka-server-stop.sh
	else
#		Stopgap till /kafka softlink is created during the next Docker build to remove version specific directories inside the docker scripts
		if [ -d /kafka_2.11-1.1.0 ]
		then
			/kafka_2.11-1.1.0/bin/kafka-server-stop.sh
		fi
		if [ -d /kafka_2.11-1.1.1 ]
		then
			/kafka_2.11-1.1.1/bin/kafka-server-stop.sh
		fi
	fi	
#	Stop Kibana and ElasticSearch
	/etc/init.d/kibana stop
	/etc/init.d/elasticsearch stop
#	Stop Zookeeper
	/etc/init.d/zookeeper stop
#
fi
#
if [ "$SMdockerSIMMODE" == "-sim" ]
then
	echo "Bypassing GPIO controls in simulation mode ...."
else
	if [ -d /docker/src/DevAbs ]
	then
		cd /docker/src/DevAbs
		echo ""
		echo "!!!IMPORTANT!!! Turning Off Dock Fans ...."
# 		PLC IP Addresses and bitmaps are hardcoded for XM1, XM2 and XM3
		./dockergpiowheelerctlrclidirect 192.168.1.177 -wr 0
		echo ""
#
		echo ""
		echo "!!!IMPORTANT!!! Turning Off All Charger Contactors and HVAC ...."
# 		PLC IP Addresses and bitmaps are hardcoded for XM1, XM2 and XM3
		./dockergpiowheelerctlrclidirect 192.168.1.177 -wd 10000
		echo ""
#
		echo ""
		echo "!!!!!IMPORTANT!!!!! Turning Off MPCC ...."
# 		PLC IP Addresses and bitmaps are hardcoded for XM1, XM2 and XM3
		./dockergpiowheelerctlrclidirect 192.168.1.177 -wr 0
		echo ""
#
	else
		dockerdocker=`docker ps | grep docker | grep -v grep | awk '{print$1}'`
		if [ ! -z $dockerdocker ]
		then
			echo "Terminating docker container docker with ID: " $dockerdocker
			docker exec -it $dockerdocker bash -c "${ENTRY_POINT}"
			docker stop $dockerdocker
		fi
	fi
fi
#

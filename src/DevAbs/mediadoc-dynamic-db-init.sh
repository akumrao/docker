#
esdbstate="red"
esdbhealth=""
esdberror=""
echo "Waiting for ES DB Cluster Shards/Segments and Indices to be Initialized. Wait for health to change from red to yellow"
while [ "$esdbstate" = "red" ]
	do echo -n " .... "
	esdbstate=`curl -XGET localhost:9200/_cat/health -s 2>&1 | grep -v grep | awk '{print $4'} | grep red`
	esdbhealth=`curl -XGET localhost:9200/_cat/health -s 2>&1 | grep -v grep | awk '{print $4'}`
	esdberror=`curl -XGET localhost:9200/_cat/health 2>&1 | grep -v grep | grep refused`
	if [ "$esdberror" != "" ]
	then
		echo "!!! ES DB Initialization Error. Please call Station Cloud Operations to potentially restart CCU Docker Container !!!"
		echo -n " .... "
		echo "!!! Automatically attempting restart of ES DB !!!"
		/etc/init.d/elasticsearch restart
		echo "Waiting 120 secs for ElasticSearch re-initialization ...."
		sleep 120;
		esdbstate="red"
		esdbhealth=""
		esdberror=""
	else 
		echo "[ Checking ES DB Health every 20 secs: " $esdbhealth " ]"
	fi
	sleep 20;
done;
echo ""
echo ""
echo "ES DB Cluster is now Ready. Proceeding to DB/Index Initialization"
echo ""
#
echo ""
echo "Initializing BLE MAC DB ..."
curl -XDELETE localhost:9200/media-dynamic-blemac > /dev/null 2>&1
echo ""
curl -XPUT localhost:9200/media-dynamic-blemac
echo ""
#
echo ""
echo "Initializing HVAC DB ..."
curl -XDELETE localhost:9200/media-dynamic-hvac 2>&1
echo ""
curl -XPUT localhost:9200/media-dynamic-hvac
echo ""
#
for xmid in `seq 1 3`; 
	do instr="curl -XPOST -H \"Content-type:application/json\" localhost:9200/media-dynamic-hvac/data/qis.xm.$xmid.hvac -d '{ \"model-name\":\"qis.xm.$xmid.hvac\", \"wotTempSensorFault\":\"off\", \"evaporatorInTempSensorFault\":\"off\", \"highPressureAlarm\":\"off\", \"highPressureManualAlarm\":\"off\", \"eitHighTempAlarm\":\"off\", \"eitLowTempAlarm\":\"off\", \"eotHighTempWarning\":\"off\", \"eotLowTempWarning\":\"off\"}'";
	command="$(echo $instr)";
	eval $command;
	echo ""
done
#
echo ""
echo "Initializing ENERGYMETER DB ..."
curl -XDELETE localhost:9200/media-dynamic-energymeter > /dev/null 2>&1
echo ""
curl -XPUT localhost:9200/media-dynamic-energymeter
echo ""
#
for xmid in `seq 1 3`; 
	do instr="curl -XPOST -H \"Content-type:application/json\" localhost:9200/media-dynamic-energymeter/data/qis.xm.$xmid.energymeter -d '{ \"model-name\":\"qis.xm.$xmid.energymeter\", \"voltageAn\":-1.0, \"voltageBn\":-1.0, \"voltageCn\":-1.0, \"voltageLn\":-1.0, \"currentA\":-1.0, \"currentB\":-1.0, \"currentC\":-1.0, \"currentN\":-1.0, \"powerFactorA\":-1.0, \"powerFactorB\":-1.0, \"powerFactorC\":-1.0, \"powerFactorT\":-1.0, \"frequency\":-1.0 }'";
	command="$(echo $instr)";
	eval $command;
	echo ""
done
#
echo ""
echo "Initializing SAFETY DB ..."
curl -XDELETE localhost:9200/media-dynamic-safety > /dev/null 2>&1
echo ""
curl -XPUT localhost:9200/media-dynamic-safety
echo ""
#
for xmid in `seq 1 3`; 
	do instr="curl -XPOST -H \"Content-type:application/json\" localhost:9200/media-dynamic-safety/data/qis.xm.$xmid.safety -d '{ \"model-name\":\"qis.xm.$xmid.safety\", \"fdss\":\"fire\", \"mccbt\":\"tripped\", \"bdlss\":\"open\"}'";
	command="$(echo $instr)";
	eval $command;
	echo ""
done
#
echo ""
initbpdockdb="$(echo $1)"
if [ "$initbpdockdb" = "initbpdockdb" ]
then
	echo "<< Option to force initialization of BATTERY PACK DOCK DB provided >>>"
	echo ""
	bpdockdbstate=""
else
	echo "<< Checking if BATTERY PACK DOCK DB exists >>>"
	echo ""
	bpdockdbstate=`curl -XGET localhost:9200/media-dynamic-bp/data/_search 2>&1 | grep "hits\":{\"total" | awk -F "[,:]" '{print $16}'`
fi
if [ -z $bpdockdbstate ]
then
	echo "Initializing BATTERY PACK DOCK DB ..."
	curl -XDELETE localhost:9200/media-dynamic-bp > /dev/null 2>&1
	echo ""
	curl -XPUT localhost:9200/media-dynamic-bp
	echo ""
#
	for xmid in `seq 1 3`; 
		do for sdockid in `seq 1 15`; 
			do instr="curl -XPOST -H \"Content-type:application/json\" localhost:9200/media-dynamic-bp/data/qis.xm.$xmid.sdock.$sdockid.battery -d '{ \"model-name\":\"qis.xm.$xmid.sdock.$sdockid.battery\", \"bpid\":\"\", \"soc\":-1.0, \"packvoltage\":-1.0, \"maxtemp\":-1.0, \"mintemp\":-1.0, \"balancingstatus\":0, \"ttc\":-1, \"comm-status\":\"error\", \"admin-state\":\"disabled\" }'";
			command="$(echo $instr)";
			eval $command;
			echo "";
		done;
	done;
	echo ""
else
	echo "No changes to existing BATTERY PACK DOCK DB ..."
	echo ""
fi
initclouddb="$(echo $2)"
if [ "$initclouddb" = "initclouddb" ]
then
	echo "<< Option to force initialization of CLOUD DB provided >>>"
	echo ""
	clouddbstate=""
else
	echo "<< Checking if CLOUD DB exists >>>"
	echo ""
	clouddbstate=`curl -XGET localhost:9200/media-dynamic-cloud/data/_search 2>&1 | grep "hits\":{\"total" | awk -F "[,:]" '{print $16}'`
fi
if [ -z $clouddbstate ]
then
	echo "Initializing CLOUD DB ..."
	curl -XDELETE localhost:9200/media-dynamic-cloud > /dev/null 2>&1
	echo ""
	curl -XPUT localhost:9200/media-dynamic-cloud
	echo ""
#
else
	echo "No changes to existing CLOUD DB ..."
	echo ""
fi

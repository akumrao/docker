import json
import time
import threading
import traceback

from kafka import KafkaConsumer, KafkaProducer

class KafkaManager:
    def __init__(self, config):
        self.__config = config
        self.__producer = KafkaProducer(value_serializer=lambda m: json.dumps(m).encode('utf8'), bootstrap_servers = config.get('bootstrap_servers'))

    @staticmethod
    def createKfMsgKey():
        millis = int(round(time.time() * 1000))
        return millis
        # return str(millis)

    @staticmethod
    def createTxIdKey():
        timeStr = format(time.time(), '.6f').replace('.', '-')
        return timeStr

    def kafkaProducer(self, topic, payload):
        self.__producer.send(topic, payload)
        self.__producer.flush()

    def startConsumer(self, callback):
        self._consumerThread = threading.Thread(target=self._subscriberThread, args=(callback,))
        self._consumerThread.daemon = True
        self._consumerThread.start()

    def _subscriberThread(self, callback):
        self.__consumer = KafkaConsumer(bootstrap_servers = self.__config.get('bootstrap_servers'), group_id = self.__config.get('group_id'), max_poll_interval_ms = 1000, max_poll_records = 100, auto_offset_reset="latest", )
        self.__consumer.subscribe(self.__config.get('topics'))	
        for msg in self.__consumer:
            print("msg: {}".format(msg))
            try:
                callback(msg.topic, json.loads(msg.value.decode('utf8')))
                self.__consumer.commit()
            except Exception as e:
                traceback.print_exc()

    def sendLog(self, payload):
        msg = {
			"media-time": self.createKfMsgKey(),
 			"media-txIdKey":self.createTxIdKey(),
 			"media-source" : {
				"type":"LOCAL-APP",
				"address":payload.get("application_name")
 			},
 			"media-recordType": "WHEELER-LOG-MSG",
 			"media-data" : {
				"log-message" : {
					"subsystem" : payload.get('subsystem'),
					"level": payload.get('level'),#"emergency | alert | critical | error | notice | info | debug",
					"text-message": payload.get('text-message'),
					"json-message": payload.get('json-message'),
				}
 			}
		}
        self.__producer.send("ccuapp-to-log", msg)
 

#!/bin/bash
DAYS_KEPT=90
INDICES='media-2'
###############
### DO NOT MESS WITH THIS SCRIPT BELOW HERE UNLESS YOU KNOW WHAT YOU ARE DOING
###############
# Intentionally using %d instead of %e for Zero padding
EPOC=$(date --date="${DAYS_KEPT} days ago" +%Y%m%d)
ALL_LINES=$(/usr/bin/curl -s -XGET http://127.0.0.1:9200/_cat/indices\?v | egrep ${INDICES} | egrep close)
echo "${ALL_LINES}" | while read LINE
do
	FORMATED_LINE=$(echo $LINE | awk '{ print $2 }' | awk -F'-' '{ print $2 }' | sed 's/\.//g')
	if [ "${FORMATED_LINE}" != "" ]
	then
		if [ "${FORMATED_LINE}" -lt "${EPOC}" ]
		then
			TO_DELETE=$(echo ${LINE} | awk '{ print $2 }')
			echo "... Deleting Closed ElasticSearch Index (older than ${DAYS_KEPT} days from now): http://127.0.0.1:9200/${TO_DELETE}"
			/usr/bin/curl -XDELETE http://127.0.0.1:9200/${TO_DELETE} > /dev/null 2>&1
		fi
	fi
done

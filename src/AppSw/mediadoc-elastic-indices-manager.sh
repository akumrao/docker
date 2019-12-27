#
# This script periodically closes indices to relieve memory pressure on ElasticSearch
# and also deletes closed indices that are no longer needed for Station Debug and Operations
#
set -x
while true;
	do 
	/ccu/src/DevAbs/mediadoc-close-elastic-indices.sh
	/ccu/src/DevAbs/mediadoc-delete-elastic-indices.sh
	sleep 86400
done;
#

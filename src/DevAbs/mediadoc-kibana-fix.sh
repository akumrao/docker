#
echo ""
echo "TEMPORARY Fix for Kibana 6.5.x issues. Refer https://discuss.elastic.co/t/kibana-server-not-ready/162075"
echo ""
curl -XDELETE localhost:9200/.kibana_1
echo ""
curl -XDELETE localhost:9200/.kibana_2
echo ""
/etc/init.d/kibana restart
echo ""
echo "!!!! <<<< PLEASE REDEFINE INDEX PATTERN \"media-2*\" with timestamp set as \"@timestamp\" and then REIMPORT ALL DASHBOARDS >>>> !!!!"
echo ""

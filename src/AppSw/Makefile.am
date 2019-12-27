#For Wheeler BP BETA Aug 2018
#AM_CPPFLAGS=-std=gnu++11 -Wall -Werror -I ../../open-src -I ../OsEncap -I /libcrc-master/include -I /cppkafka-master/include/cppkafka/ -O0 -Dmediadoc_BLE_MULTI_WRITE -Dmediadoc_WHEELER_BP_BETA_2018 -D_REENTRANT
#Optimized SWAP with BP BETA Aug 2018
AM_CPPFLAGS=-std=gnu++11 -Wall -Werror -I ../../open-src -I ../OsEncap -I /libcrc-master/include -I /cppkafka-master/include/cppkafka/ -O0 -Dmediadoc_BLE_MULTI_WRITE -Dmediadoc_WHEELER_BP_BETA_2018 -Dmediadoc_OPTIMIZED_SWAP -D_REENTRANT
#For Wheeler BP ALPHA Mar 2018
#AM_CPPFLAGS=-std=gnu++11 -Wall -Werror -I ../../open-src -I ../OsEncap -I /libcrc-master/include -I /cppkafka-master/include/cppkafka/ -O0 -Dmediadoc_BLE_MULTI_WRITE -D_REENTRANT
#
AM_LDFLAGS=-lcppkafka -lrdkafka ../OsEncap/libosencap.a -lble++ /libcrc-master/lib/libcrc.a -lrt -pthread -D_REENTRANT
LDADD=-lcppkafka -lrdkafka ../OsEncap/libosencap.a -lble++ /libcrc-master/lib/libcrc.a -lrt

bin_PROGRAMS = energy 
ccuhealthwheelerorch_SOURCES = CcuKafkaMessage.cpp 

#!/bin/bash

 
set -ex

ROOT_DIR=$(cd $(dirname $0) && pwd)
cd ${ROOT_DIR}

if ! grep docker /etc/hosts; then
        cat /etc/hosts.docker >> /etc/hosts
fi

#if ! grep 8.8.8.8 /etc/resolv.conf; then
#	echo "nameserver 8.8.8.8" >> /etc/resolv.conf
#fi

# CTags
cd /docker/src && ctags -R . > /dev/null 2>&1

# dockerUI
#pip3 install -r /docker/dockerUI/requirements.txt
# docker source
cd /docker/src/OsEncap && ./mediadocker-builds.sh
cd /docker/src/DevAbs && ./mediadocker-builds.sh
cd /docker/src/AppSw && ./mediadocker-builds.sh
cd /docker/dockerUI/www && npm install
cd /docker/dockerUI/www/src && npm install
#pip3 install -r /docker/dockerUI/requirements.txt
#cd /docker/dockerUI/www/src && coffee -bmc *.coffee

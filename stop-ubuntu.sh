#!/bin/bash
set -x
#stop docker container
echo "Switching off Docker..."
./stop-container.sh

i=0
while [ $i -eq 0 ]
do
    if docker ps | grep "ccu" > /dev/null
    then
        echo "Docker is Running..."
        i=0
    else
        echo "Docker is Stopped.."
        i=1
    fi
    sleep 10
done

if [ $1=="restart" ]
then
    echo "Restarting"
    sudo shutdown now
elif [ $1=="shutdown"]
then
    echo "Shutting Down"
    sudo reboot
fi


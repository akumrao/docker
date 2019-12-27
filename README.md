# README



> The Following is the guide to Setup Media server with Kafaka.

Take AWS, Amazon, Blade or NUC

## Install Ubuntu 18.04 LTS and Setup
*	Step 1 : Create bootable USB	
	*	[GUIDE TO CREATE BOOTABLE USB for WINDOWS](http://www.linuxandubuntu.com/home/make-ubuntu-bootable-usb-in-windows-10)
	*	[GUIDE TO CREATE BOOTABLE USB for LINUX](https://tutorials.ubuntu.com/tutorial/tutorial-create-a-usb-stick-on-ubuntu#0)
*	step 2 : Ubuntu 18.04 Installation 
	*	[Installation GUIDE](https://tutorials.ubuntu.com/tutorial/tutorial-install-ubuntu-desktop#0)
		*	(Select option  "install third party software for graphics and wifi hardware")
		*	Time-zone -- kolkata
		*	**name-`media` , computer's name-`media-doc` , username-`media` , password-`media123` (ALL lower CASE letters)**
		*	Enable auto-login option
*   Step 3 : Turn-Off display 
	*	[PREVENT DISPLAY SLEEPING AND TURN OFF LOCKSCREEN](https://websiteforstudents.com/disable-turn-off-ubuntu-18-04-lts-beta-lock-screen/)
	*	disable showing notification on lockscreen.
*   Step 4 : Set Static IP for Ethernet
	*	[SET STATIC IP FOR ETHERNET](https://linuxconfig.org/how-to-configure-static-ip-address-on-ubuntu-18-04-bionic-beaver-linux)
	*	Station ip : `192.168.1.2`
	*	Netmask : `255.255.255.0`
*	Step 5 : Connect to WIFI `for internet`(**THIS IS OPTIONAL**)
*	Step 6 : Setup wake on Power
	*   `FOR MOOTECH BOX PC`
    *	Go to BIOS ( Press ESC after power-on )
	*	Goto **CHIPSET**>**PCH-IO Configuration**>**State afet G3** -- make it "**S0 state**"
README.md	*   For intel NUC , go to BIOS > POWER > State after power failure > Last State and disable SECURE boot
    *	Save Changes and Exit from BIOS



## Docker Setup


### Run the following commands 
*	`sudo apt update`
*	`sudo apt upgrade`
*	`sudo apt install -y vim zsh git make curl apt-transport-https ca-certificates software-properties-common openssh-server sendip tcpdump bluez python-pip python3-pip python


sudo apt-get remove docker docker-engine docker.io
Step 3: Install Docker
To install Docker on Ubuntu, in the terminal window enter the command:

sudo apt install docker.io
Step 4: Start and Automate Docker
The Docker service needs to be setup to run at startup. To do so, type in each command followed by enter:

sudo systemctl start docker
sudo systemctl enable docker




### Clone Docker Repo
*	`git clone https://github.com/akumrao/docker.git`
*   `git submodule init`
*   `git submodule update`
*   `cd docker/`
**   `cd ..`
*	`make install` **(System will restart after this step)**,**(Execute this step only for the Initial Setup)** ,**(Do Not Run this on a Dev System, or personal laptops)**
*	`make build-docker-image` **(Instead of this , you may follow docker image build steps at the bottom of this readme)**
*	`cd ~/docker`
*	`./start-container.sh /docker/src/build-all.sh` **(Run this for building the code)**
*	`./start-container.sh` **(Run this for Starting Container)**

docker ps
docker attach  psid
docker exec -it  065524c4b9af /bin/bash

### Help

*	docker starts up **automatically** when the PC wakesup.
*	You need to attach to docker container for development or testing by running command `docker attach sun` + 	`TAB` button  (docker name is mediaCCU-dAtETiMe).
*	detach from docker -- `ctrl+P` +  `ctrl+Q`, if you want to attach back , user `docker attach media` + `TAB`
*	detach from screen -- `ctrl+a` +  `d`, if you want to attach back to screen , use `screen -r `
*	to prevent ui from automatically starting , run the command  `touch /home/${USER}/nokiosk` in home directory.




## Also possible with Docker Image

Please avoid `make build-docker-image`. It takes around one hours to build docker. Better copy from Link.

Please Use the following link to get the latest docker image:
> Version Controling will be done using the Datetime of upload

[ Link to Download Docker Image](https://xxxx.com)



Open terminal in the folder where the file is downloaded
Load image using : `docker load -i <docker-image-filename>`
RUN: `docker tag  $(docker images | grep -A 1 "IMAGE ID" | awk '{getline; print $3}') docker:latest`


#### kibana 
*   `service kibana stop`
*   `curl -XDELETE http://localhost:9200/.kibana_x` where `x` is an interger from 1 to 3 
*	`service kibana start`



Actions to be taken when docker went through an improper shutdown and ES DB shards are not turning yellow:

1:start the container
2:goto src
3:start startallservices
4:wait for ES to start
5:stop the startallservices when ES gets started(ctrl c the start all)
6:Run the following command to check if ES got started 
curl -XGET localhost:9200/_cat/indeices?v | more 
7:go to ES location
/var/lib/elasticsearch
8:check log files
9: if something is corrupted , run the following command
mv node node.corrupt
10:start container again
11:re-import jsons for dashboards



To compile Media Service Interacting with Kafka

git clone https://github.com/akumrao/mediaserver.git 

cd mediaserver/src/net/kafka

git clone https://github.com/mfontanini/cppkafka.git
cppkafka

cmake -DCMAKE_BUILD_TYPE=Debug  -DCPPKAFKA_BUILD_SHARED=0  ..

librdkafka
https://github.com/edenhill/librdkafka.git

./configure --enable-devel   --enable-devel

make



for running kafka

localhost:56001

for clean kafka/kibana indices
curl -XDELETE 0:9200/media-\*

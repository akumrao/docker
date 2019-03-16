
IMAGE_TAG=ccu

ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

.PHONY: build-docker-image
build-docker-image:
	find src/ -name "*core.*ccu*" -exec rm -f {} \;
	docker build $(ROOT_DIR) -t $(IMAGE_TAG)

.PHONY: install
install:
	stationid=`cat /home/sunm/ccu/setup/config.yaml| grep serial_number | awk '{print $2}'| head -1`; sudo hostnamectl set-hostname $stationid;
	wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
	echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list
	sudo cp -v sunmccu-container.service /etc/systemd/system/
	sudo cp -v /home/sunm/ccu/runscreenrc.sh.desktop /home/sunm/.config/autostart/
	sudo chmod 664 /etc/systemd/system/sunmccu-container.service
	sudo systemctl enable sunmccu-container.service
	sudo apt-get install google-chrome-stable
	sudo apt install net-tools curl docker.io screen
	sudo apt update
	sudo apt upgrade
	ssh-keygen
	ssh-copy-id canlogger@13.71.21.73
	sudo usermod -aG docker $(USER)
	crontab -l > mycron
	echo "0 */1 * * * /home/${USER}/ccu/utilities/plc_rtc/rtc.py" >> mycron
	crontab mycron
	rm mycron
	sudo cp -v setup/kiosk/ccu-gui-kiosk.sh.desktop /home/sunm/.config/autostart/
	echo -e "blacklist pn533\nblacklist pn533_usb\nblacklist nfc"| sudo tee /etc/modprobe.d/blacklist-libnfc.conf
	echo -e "Restarting the system.............."
	sleep 10s
	sudo reboot

#.PHONY: test-docker-image
#test-docker-image:
   #echo "$(ROOT_DIR)/start-container.sh $(ROOT_DIR) $(IMAGE_TAG)"
    #docker run --mount type=bind,source=$(ROOT_DIR),destination=/ccu --mount source=es,destination=/var/lib/elasticsearch --mount source=es,destination=/var/log/elasticsearch -v /dev/bus/usb\:/dev/bus/usb --privileged --net=host --security-opt seccomp:unconfined -it $(IMAGE_TAG)
    #docker run --mount type=bind,source=$(ROOT_DIR),destination=/ccu --mount source=es,destination=/var/lib/elasticsearch --mount source=es,destination=/var/log/elasticsearch --privileged -v "/dev/bus/usb:/dev/bus/usb" --net=host --security-opt seccomp:unconfined -it $(IMAGE_TAG)

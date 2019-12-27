
IMAGE_TAG=docker

ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

.PHONY: build-docker-image
build-docker-image:
	find src/ -name "*core.*docker*" -exec rm -f {} \;
	docker build $(ROOT_DIR) -t $(IMAGE_TAG)

.PHONY: install
install:
	stationid=`cat /home/media/docker/setup/config.yaml| grep serial_number | awk '{print $2}'| head -1`; sudo hostnamectl set-hostname $stationid;
	wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
	echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list
	sudo cp -v mediadoc-container.service /etc/systemd/system/
	sudo cp -v /home/media/docker/runscreenrc.sh.desktop /home/media/.config/autostart/
	sudo chmod 664 /etc/systemd/system/mediadoc-container.service
	sudo systemctl enable mediadoc-container.service
	sudo apt-get install google-chrome-stable
	sudo apt install net-tools curl docker.io screen
	sudo apt update
	sudo apt upgrade
	ssh-keygen
	sudo usermod -aG docker $(USER)
	crontab -l > mycron
	echo "0 */1 * * * /home/${USER}/docker/utilities/plc_rtc/rtc.py" >> mycron
	crontab mycron
	rm mycron
	echo -e "blacklist pn533\nblacklist pn533_usb\nblacklist nfc"| sudo tee /etc/modprobe.d/blacklist-libnfc.conf
	echo -e "Restarting the system.............."
	sleep 10s
	sudo reboot

#.PHONY: test-docker-image
#test-docker-image:
   #echo "$(ROOT_DIR)/start-container.sh $(ROOT_DIR) $(IMAGE_TAG)"
    #docker run --mount type=bind,source=$(ROOT_DIR),destination=/docker --mount source=es,destination=/var/lib/elasticsearch --mount source=es,destination=/var/log/elasticsearch -v /dev/bus/usb\:/dev/bus/usb --privileged --net=host --security-opt seccomp:unconfined -it $(IMAGE_TAG)
    #docker run --mount type=bind,source=$(ROOT_DIR),destination=/docker --mount source=es,destination=/var/lib/elasticsearch --mount source=es,destination=/var/log/elasticsearch --privileged -v "/dev/bus/usb:/dev/bus/usb" --net=host --security-opt seccomp:unconfined -it $(IMAGE_TAG)

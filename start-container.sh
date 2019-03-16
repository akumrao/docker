#!/bin/sh


ENTRY_POINT="${1:-/ccu/src/start-all-services.sh}"
NAME="sunmccu-$(date +%Y%m%d%H%M%S)"
IMAGE_TAG="ccu"
ROOT_DIR=$(cd $(dirname $0) && pwd)


echo "Cleaning up exited containers..."
docker rm $(docker ps -a | awk '/Exited /{print $1}'  )
set -ex

echo "Starting CCU container ${NAME}..."
docker run --mount type=bind,source=${ROOT_DIR},destination=/ccu --mount source=es,destination=/var/lib/elasticsearch --mount source=es,destination=/var/log/elasticsearch -v /dev:/dev --privileged --net=host -v /var/lib/bluetooth:/var/lib/bluetooth  -v /var/run/dbus:/var/run/dbus -v /sys/class/bluetooth:/sys/class/bluetooth  -v /sys/fs/cgroup:/sys/fs/cgroup:ro --cap-add=SYS_ADMIN --cap-add=SYS_ADMIN --security-opt seccomp:unconfined --name "${NAME}" ${DOCKER_OPTS:--d} -it ${IMAGE_TAG} ${ENTRY_POINT}

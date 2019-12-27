#!/bin/sh


ENTRY_POINT="${1:-/docker/src/start-all-services.sh}"
NAME="mediadocker-$(date +%Y%m%d%H%M%S)"
IMAGE_TAG="docker"
ROOT_DIR=$(cd $(dirname $0) && pwd)


echo "Cleaning up exited containers..."
docker rm $(docker ps -a | awk '/Exited /{print $1}'  )
set -ex

echo "Starting docker container ${NAME}..."
docker run --mount type=bind,source=${ROOT_DIR},destination=/docker --mount source=es,destination=/var/lib/elasticsearch --mount source=es,destination=/var/log/elasticsearch -v /dev:/dev --privileged --net=host -v /var/lib/bluetooth:/var/lib/bluetooth  -v /var/run/dbus:/var/run/dbus -v /sys/class/bluetooth:/sys/class/bluetooth  -v /sys/fs/cgroup:/sys/fs/cgroup:ro --cap-add=SYS_ADMIN --cap-add=SYS_ADMIN --security-opt seccomp:unconfined --name "${NAME}" ${DOCKER_OPTS:--d} -it ${IMAGE_TAG} ${ENTRY_POINT}

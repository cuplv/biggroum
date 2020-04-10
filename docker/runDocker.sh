#!/bin/bash
echo "Mounting $1"
docker run -it --rm --mount type=bind,source=${1},target=/home/biggroum/data biggroum:latest bash

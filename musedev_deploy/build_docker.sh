#!/bin/bash
cp ../python/fixrgraph/musedev/setup_docker.sh .
docker build -t fixrgraph_muse:latest .
rm setup_docker.sh


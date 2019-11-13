#!/bin/bash

apt install -y wget python-pip
pip install nose requests
wget https://github.com/cuplv/FixrGraphExtractor/releases/download/v1.0-musedev/fixrgraphextractor_2.12-0.1.0-one-jar.jar
git clone https://github.com/cuplv/biggroum.git
cd biggroum && git checkout musedev_hackaton && git pull
PYTHONPATH="${PYTHONPATH}:/opt/biggroum/python"
GRAPHEXTRACTOR="/opt/fixrgraphextractor_2.12-0.1.0-one-jar.jar"
touch /opt/setup_complete

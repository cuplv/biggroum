#!/bin/bash


echo "Check that you are connected to the VPN..."
docker login http://100.120.0.2:5005

docker tag biggroum_search 100.120.0.2:5005/biggroum_search:0.1
docker push 100.120.0.2:5005/biggroum_search:0.1

docker tag biggroum_solr 100.120.0.2:5005/biggroum_solr:0.1
docker push 100.120.0.2:5005/biggroum_solr:0.1

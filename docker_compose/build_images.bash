#!/bin/bash

# Solr
pushd .
cd ../FixrGraphPatternSearch/docker_solr
bash download_data.bash
docker build -t biggroum_solr .

# Search
popd
pushd .
cd ../FixrGraphPatternSearch/docker_search
bash download_data.bash
docker build -t biggroum_search .


# src server
popd
pushd .
cd ../fixr_source_code_service/docker/
docker build -t srcfinder .
popd

# web interface
popd
pushd .
cd ../fixr_source_code_service/docker/
docker build -t biggroum_frontend .
popd

#!/bin/bash

# Search
pushd .
cd ../FixrGraphPatternSearch/docker_search
# bash download_data.bash
docker build -t biggroum_search .
popd

# src server
pushd .
cd ../fixr_source_code_service/docker/
docker build -t srcfinder .
popd

# web interface
pushd .
cd ../fixr_groum_search_frontend/docker/
docker build -t biggroum_frontend .
popd

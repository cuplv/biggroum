#!/bin/bash
docker tag biggroum_search cuplv/biggroum_search:latest
docker tag srcfinder cuplv/srcfinder:latest
docker push cuplv/biggroum_search:latest
docker push cuplv/srcfinder:latest

#!/bin/bash

version=2.0

echo "Check that you are connected to the VPN..."
docker login http://100.120.0.2:5005

docker tag biggroum_search 100.120.0.2:5005/biggroum_search:${version}
docker push 100.120.0.2:5005/biggroum_search:${version}

docker tag srcfinder 100.120.0.2:5005/srcfinder:${version}
docker push 100.120.0.2:5005/srcfinder:${version}

docker tag biggroum_frontend 100.120.0.2:5005/biggroum_frontend:${version}
docker push 100.120.0.2:5005/biggroum_frontend:${version}

# Generate the docker-compose.yml file
python get_docker_compose.py -r ${version}

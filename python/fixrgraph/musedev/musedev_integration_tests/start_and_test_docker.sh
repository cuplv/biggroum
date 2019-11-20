#!/bin/bash
pushd .

cd "$(dirname "${BASH_SOURCE[0]}")/../../../../docker_compose/"

# Get docker compose for integration tests
python get_docker_compose.py --remote -v latest -m -d

docker-compose up --force-recreate --detach

bash ../python/fixrgraph/musedev/musedev_integration_tests/test_docker.sh docker_compose_fixrgraph_1

docker-compose down

popd

#!/bin/bash
pushd .

cd "$(dirname "${BASH_SOURCE[0]}")/../../../../docker_compose/"

# Get docker compose for integration tests
python get_docker_compose.py --remote -v latest -m -d

docker-compose up --force-recreate &

function wait_for_container {
	while [[ ! $(docker ps |grep $1) ]]
	do
		sleep 2
		echo "Waiting for containers to start..."
	done
}

wait_for_container "compose_fixrgraph"
wait_for_container "compose_srcfinder"

ANALYST_NAME=$(docker ps --format "{{.Names}}" |grep fixrgraph)

bash ../python/fixrgraph/musedev/musedev_integration_tests/test_docker.sh ${ANALYST_NAME}

docker-compose down

popd

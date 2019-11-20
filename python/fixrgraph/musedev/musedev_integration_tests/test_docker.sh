#!/bin/bash
## Run Docker Container

CONTAINER_NAME=$1
shift
## Copy biggroum script and app
BASE_DIR=$(dirname "${BASH_SOURCE[0]}")
docker cp "${BASE_DIR}/../biggroumcheck.sh" ${CONTAINER_NAME}:/root/
! (docker exec -it ${CONTAINER_NAME} bash -c "ls /root/AwesomeApp.zip 2>/dev/null 1>/dev/null") && \
	docker cp "${BASE_DIR}/../test/data/AwesomeApp.zip" ${CONTAINER_NAME}:/root/
! (docker exec -it ${CONTAINER_NAME} bash -c "ls /root/AwesomeApp 2>/dev/null 1>/dev/null") && \
	docker exec -it ${CONTAINER_NAME} /bin/bash -c "cd /root/ && unzip /root/AwesomeApp.zip > /dev/null"

## Run tests
# $1 file containing command input
# $2 command (version, finalize, applicable)
# $3 reference output
function run_test {
	INPUT_FILE="$(dirname "${BASH_SOURCE[0]}")/$1"
	COMMAND=$2
	OUTPUT_FILE="$(dirname "${BASH_SOURCE[0]}")/$3"
	echo "====Running command: $COMMAND"
	echo "=input:"
	echo $(cat $INPUT_FILE)
	echo "="
	TMPFILE=$(mktemp)
	cat $INPUT_FILE | docker exec -i ${CONTAINER_NAME} /bin/bash -c "/root/biggroumcheck.sh /root/AwesomeApp 1245abc $COMMAND" 1>"$TMPFILE" 2>> "${BASE_DIR}/error_log"
	
	# Check that the reference file contains equivilant json to the command output
	# Note: this avoids issues with whitespace and ordering
	cat $TMPFILE | jq . >> /dev/null
	if [ $? -ne 0 ]
       	then 
		echo "-------------------Command $COMMAND: Failed"
	else
		if [[ $3 == "strict" ]]
		then
			if [[ $(cmp <(jq -cS . $OUTPUT_FILE) <(jq -cS . $TMPFILE)) ]]
			then
				echo "-------------------Command $COMMAND: Failed"
			else
				echo "-------------------Command $COMMAND: OK"
			fi
		fi
	fi
	echo "=output:"
	cat $TMPFILE
	printf "\n="
	echo "=expect output:"
	echo $(cat $OUTPUT_FILE)
}

# Output of version, applicable, and run must be exact
run_test "example_version_input.json" "version" "expected_version_output.json" strict
run_test "example_applicable_input.json" "applicable" "expected_applicable_output.json" strict
run_test "example_run_input.json" "run" "example_run_output.json" strict

# Accept any valid json for finalize
run_test "example_finalize_input.json" "finalize" "example_finalize_output.json" any 

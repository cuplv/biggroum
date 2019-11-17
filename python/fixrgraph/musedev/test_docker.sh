docker run -e "PYTHONPATH=/root/biggroumsetup/biggroum/python" -e"GRAPH_EXTRACTOR_PATH=/root/biggroumsetup/fixrgraphextractor_2.12-0.1.0-one-jar.jar" --rm -d --name fixrgraph_deploy musedev/analyst bash -c "sleep 1200"
docker cp biggroumcheck.sh fixrgraph_deploy:/root/
docker cp /Users/s/Documents/source/biggroum/python/fixrgraph/musedev/test/data/AwesomeApp.zip fixrgraph_deploy:/root/
docker exec -it fixrgraph_deploy /bin/bash -c "cd /root/ && unzip /root/AwesomeApp.zip"


function run_test {
	CMD_OUT=$(cat $1 | docker exec fixrgraph_deploy /bin/bash -c "/root/biggroumcheck.sh /root/AwesomeApp 1245abc $2")
	
	if [[ $CMD_OUT == $3 ]]
	then
		echo "Command $1: OK"
	else
		echo "Command $1: Failed"
		echo "    expected: $3"
		echo "    actual: $CMD_OUT"
	fi


}

run_test "example_version_residue.txt" "version" "3"
run_test "example_version_residue.txt" "applicable" "true"

docker kill fixrgraph_deploy

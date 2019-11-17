docker run -e"GRAPH_EXTRACTOR_PATH=/root/biggroumsetup/fixrgraphextractor_2.12-0.1.0-one-jar.jar" --rm -d --name fixrgraph_deploy musedev/analyst bash -c "sleep 300"
docker cp biggroumcheck.sh fixrgraph_deploy:/root/
docker cp /Users/s/Documents/source/biggroum/python/fixrgraph/musedev/test/data/AwesomeApp.zip fixrgraph_deploy:/root/
docker exec -it fixrgraph_deploy /bin/bash -c "cd /root/ && unzip /root/AwesomeApp.zip"
cat example_version_residue.txt | docker exec fixrgraph_deploy /bin/bash -c "/root/biggroumcheck.sh /root/AwesomeApp 1245abc version" 
docker kill fixrgraph_deploy

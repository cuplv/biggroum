Instructions For Using the BigGroum Tapfi API
=============================================
This directory contains a set of scripts to install the BigGroum client in a docker container.  BigGroum can then be queried using the biggroumcheck.sh script.

Getting the Code and Test Data:
-------------------------------

1) Check out the BigGroum git repository `git clone https://github.com/cuplv/biggroum.git`

2) Check out the submodules of the project 
```
cd biggroum
git submodule update --init --recursive --remote
git checkout test_musedev_docker #TODO: update this to develop later
cd FixrGraphPatternSearch
git checkout musedev-integration
```

Running the Integration Tests
-----------------------------
Running the following script automatically downloads, runs, and installs the script in the docker containers required to run each command.  It will then run each command providing the required input and checking the expected output.
```
cd biggroum/python/fixrgraph/musedev/musedev_integration_tests
./start_and_test_docker.sh
```

The script takes about 2 minutes to run as it installs dependencies and runs the tests.  The output will show each command, its input, the received output, and the expected output.

Running the API Manually:
------------------------

3) Generate the Docker compose file for the Fixr search and source service (the following will use a small set of test data) 
```
cd docker_compose
python get_docker_compose.py --remote -v latest -d
```
4) Start the search service 
```
docker-compose up
```
4) Run a docker container (musedev/analyst) setting the `FIXR_SEARCH_ENDPOIN` environment variable to the deployment url of the Fixr search service.

5) Copy biggroumcheck.sh into the docker container (we put it at /root/biggroumcheck.sh).

6) Copy a built android application into the container (biggroum/python/fixrgraph/musedev/test/data/AwesomeApp.zip is in the repository and may be used).

7) Call the script.
```
/root/biggroumcheck.sh /root/AwesomeApp $HASH $COMMAND
```

The supported commands are `version`, `applicable`, `run`, and `finalize`.

At this point, the residue input data should be provided to biggroumcheck.sh script via standard input.  Data is returned via standard output.

Example inputs and outputs for each command may be found in the `biggroum/python/fixrgraph/musedev/musedev_integration_tests` directory.

Speeding up the Runtime:
-----------------------
For convenience, the biggroumcheck.sh script will install the necessary dependencies at runtime.  However, this step is skipped if the script has been run previously in the same docker container. (The version command takes the longest in the unit tests because it is installing dependencies).

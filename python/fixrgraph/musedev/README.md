# Instructions For Using the BigGroum Tapfi API

This directory contains the BigGroum's implementation of the MuseDev
API. The API allows a developer to add BigGroum as a custom tool for
the MuseDev platform (https://muse.dev).

The script [biggroumcheck.sh](biggroumcheck.sh) implements the [MuseDev
API version 3](http://)) and can be invoked as:

```
bash
$ ./biggroumcheck.sh <filepath> <commit> <command>
```

where `<command>` is one among `applicable`, `version`,
`run`,`finalize`, `talk`, `reaction`.

The Fixr service is deployed at the following location.  The environment variable FIXR_SEARCH_ENDPOINT is read by the biggroumcheck.sh script.

```FIXR_SEARCH_ENDPOINT="http://3.135.214.26:8081/process_muse_data"```

Please contact us with a public ssh key to get access.

BigGroum implements the API commands as follows:
- `applicable`: returns `yes`;
- `version`: returns `3`;
- `run`: collects the compilation information and appends them in the
  residue.
- `finalize`: performs the API anomaly search and patch on the project
  contained in `<filepath>`. It uses the residue to get as input the
  path to the source files. It outputs a list of tool notes and other
  details of the analysis in the residue.
- `talk`: queries the results contained in the residue for the patch
  that should solve an anomaly and the pattern that explain an
  anomaly.
- `reaction`: does nothing and returns no output

The source code in [api.py](api.py) documents the details of each
command.


In this document we explain:
- Running Biggroum with the trymuse.sh script
- How to install the BigGroum custom tool on your repository
- The test cases we provide for the API
- How you can test the API on your local machine

## Running Biggroum with Musedev
The following assumes that you have access to the Musedev docker image and the 
`trymuse.sh` script.

To try a pre configured project, check out the repository as follows:
`git clone git@github.com:cuplv/AwesomeApp.git`

Run trymuse by changing to the directory and executing the script.  
We assume the `trymuse.sh` script has been previously downloaded to 
the current working directory. 
```
cd AwesomeApp
../trymuse.sh > ../analysis_output.json
```

### Configuring a new project
The config file should be placed in a directory at the root of the project called `.muse` and be named `config`.

The contents of this config file should be as follows:
```
build          = "gradlew"
arguments      = [ "assembleDebug" ]
jdk11          = false
androidVersion = 28
tools          = []
customTools    = [
"https://raw.githubusercontent.com/cuplv/biggroum/fix_docker/python/fixrgraph/musedev/biggroumcheck.sh"
]
```

If your project generates multiple APK files on build, please specify a build target that generates only one.
The build target is specified by the `arguments` parameter.

### Output
On success of the run, the tool will output a list of anomalies in JSON format.
```
[
  [
    {
      "tag": "CustomTool",
      "contents": "https://raw.githubusercontent.com/cuplv/biggroum/fix_docker/python/fixrgraph/musedev/biggroumcheck.sh"
    },
    {
      "tag": "ToolSuccess",
      "contents": [
```

Within the contents, each anomaly is listed.

```
          {
            "tnType": "Anomaly",
            "tnDesc": "missing method calls",
            "tnFile": "/app/src/main/java/fixr/plv/colorado/edu/awesomeapp/MainActivity.java",
            "tnLine": 49,
            "tnColumn": 0,
            "tnPatch": ...,
            "tnCodeLine": ...,
            "tnProcedure": "showDialog",
            "tnIdentifier": ...,
            "tnPhase": "PhaseUnknown",
            "tnTool": {
              "tag": "CustomTool",
              "contents": "/muse/custom-tool-scripts/biggroumcheck.sh"
            },
            "tnResidue": null
          },
```

## Installing the BigGroum custom tool on your repository
**TODO:** Document how to write a `.muse.toml` file in a
repository specifying the use of `biggroumcheck.sh` as a custom tool.
We should follow the instruction to [configure a
repository](https://docs.muse.dev/docs/repository-configuration/#inrepooptions)
from  MuseDev.


## Test Cases for the API

We test the API using the Android App
[AwesomeApp](https://github.com/cuplv/AwesomeApp) at commit
`04f68b69a6f9fa254661b481a757fa1c834b52e1`.
[AwesomeApp.zip](../test/data/AwesomeApp.zip) already contains the app
content and the related build artifact and is an example of repository
we expect to analyze with the `biggroumcheck.sh` script.

We test directly the script with the following test cases. The test
cases (and in practice only the test for `finalize`)  requires to
set the `filepath` passed to the script to the path **containing** the
folder of the Android App (e.g., the path should be `<path>` where
`<path>` contains the folder `AwesomeApp`).

We test each command of `biggroumcheck.sh` as follows:

```bash
biggroumcheck.sh <path> 04f68b69a6f9fa254661b481a757fa1c834b52e1 <command>
```

providing one of the available values for `<command>` and the following inputs (via stdin):

- applicable: [example_applicable_input.json](./musedev_integration_tests/example_applicable_input.json)

- version:  [example_version_input.json](./musedev_integration_tests/example_version_input.json)

- run:  [example_run_input.json](./musedev_integration_tests/example_run_input.json)

- finalize:  [example_finalize_input.json](./musedev_integration_tests/example_finalize_input.json)

- talk:  [example_talk_input.json](./musedev_integration_tests/example_talk_input.json)

- reaction: [example_reaction_input.json](./musedev_integration_tests/example_reaction_input.json)

The script returns the content of the following files on the standard output:

- applicable: [expected_applicable_output.json](./musedev_integration_tests/expected_applicable_output.json)

- version: [expected_version_output.json](./musedev_integration_tests/expected_version_output.json)

- run: [example_run_output.json](./musedev_integration_tests/example_run_output.json)

- finalize: [example_finalize_output.json](./musedev_integration_tests/example_finalize_output.json)

- talk: [example_talk_output.json](./musedev_integration_tests/example_talk_output.json)

- reaction (note: currently empty): [example_reaction_output.json](./musedev_integration_tests/example_reaction_output.json)


## Testing the API on a Local Machine

We describe how you can run and test the API **locally** (i.e., you
will spin up the BigGroum search services and directly invoke the
`biggroumcheck.sh` script from the analyst Docker container).

As a pre-requisite clone the BigGroum repository:
```bash
git clone https://github.com/cuplv/biggroum.git
cd biggroum
git checkout develop
git submodule update --init --recursive --remote
```

### Running the Automatic Integration Tests
The script [start_and_test_docker.sh](musedev_integration_tests ./start_and_test_docker.sh)
 automatically tests the BigGroum MuseDev API using docker containers:
```
cd biggroum/python/fixrgraph/musedev/musedev_integration_tests
./start_and_test_docker.sh
```

The script first downloads (from DockerHub) and runs the two docker containers implementing the BigGroum search services and the musedev analyst docker container (you need to
have access to the musedev/analyst image to run this container). Finally, the
script runs the test cases for the `version`, `applicable`, `run`, and
`finalize` commands.

The script takes about 2 minutes (probably more if you need to
download the images from DockerHub) to run as it installs the required
dependencies on the docker containers and runs the tests. 

The script will output each executed command, with its input, its
output, and the expected output.


### Running the API Manually

You can run the API manually following these steps (use the steps 1 and 2
if you want to deploy a local version of the Fixr search service,
otherwise go to step 3):

1) Generate the Docker compose file for the Fixr search and source code service (the following will use a small set of test data):

```
cd docker_compose
python get_docker_compose.py --remote -v latest -d
```

2) Start the search and source code service (from the same directory):
```
docker-compose up
```


3) Run the musedev/analyst docker container:

```
docker run -it musedev/analyst bash -e FIXR_SEARCH_ENDPOINT=[endpoint address]
```

  - To use the local deployment from steps 1 and 2: ```-e FIXR_SEARCH_ENDPOINT="http://localhost:8081/process_muse_data"```

  - To use our deployment: ```-e FIXR_SEARCH_ENDPOINT="http://3.135.214.26:8081/process_muse_data"```

4) Copy [biggroumcheck.sh](biggroumcheck.sh) into the docker container in `/root/biggroumcheck.sh`:

```
# get the container id
docker ps

# copy the script
docker cp biggroum/python/fixrgraph/musedev/biggroumcheck.sh [container id]:/root/
```

5) Copy a built android application into the container.

You can use the Android app in the archive
[AwesomeApp.zip](../test/data/AwesomeApp.zip). You can extract its
content in the `root` folder of the container.

```
unzip AwesomeApp.zip
docker cp AwesomeApp [container id]:/root/
```


6) Call the `biggroumcheck.sh` script:
```
/root/biggroumcheck.sh /root/AwesomeApp $HASH $COMMAND
```

At this point, you should provide the command's input data from the
command line. You can use the input data we provided above in our test
cases for the `AwesomeApp` Android app.

The output data is returned via standard output.

You can directly call the script and provide the data using the docker
run command as follows:


### Notes about the runtime
The biggroumcheck.sh script will install the necessary dependencies at
runtime (the installation of dependencies is specific for the
musedev/analyst container and will not work on other platforms). For
convenience, the installation step is skipped if the script has  been
run previously in the same docker container.


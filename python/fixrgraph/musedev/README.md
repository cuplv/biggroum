# Instructions For Using the BigGroum Tapfi API

This directory contains the BigGroum's implementation of the MuseDev
API. The API allows a developer to add BigGroum as a custom tool for
the MuseDev platform (https://muse.dev).


The entry point for the API is the script `biggroumcheck.sh`.

The script implements the MuseDev API version 3 and should be invoked
as:

```bash
$ ./biggroumcheck.sh <filepath> <commit> <command>
```

where `<command>` is one among `applicable`, `version`,
`run`,`finalize`, `talk`, `reaction`.

The detailed format of the API version 3 is documented [here](http://).

BigGroum implements the API commands commands as follows:
- `applicable`: returns always yes;
- `version`: returns `3`;
- `run`: collects the compilation information and append them in the
  residue.
- `finalize`: performs the API anomaly search and patch on the project
  contained in `<filepath>`. It uses the residue to get as input the
  path to the source files. It outputs a list of tool notes and other
  details of the analysis in the residue.
- `talk`: queries the results contained in the residue, allowing to
  inspect an anomaly, getting the patch that should solve it, and get
  the pattern explaining the anomaly.
- `reaction`: we do nothing on the reaction command.

In the following we explain:
- How to install the BigGroum custom tool on your repository
- Test cases for the API
- How you can test the API on your local machine


## Installing the BigGroum custom tool on your repository
**TODO:** Document how we can write a `.muse.toml` file in our
repository and specify the `biggroumcheck.sh` script).

We should follow the general instruction to [configure a
repository](https://docs.muse.dev/docs/repository-configuration/#inrepooptions)
from  MuseDev.


## Test cases for the API

**TODO**: The API requires to access to the service remotely at

**TODO**: the machine that access the service should be enabled via key (send us your key)?

We tested the API using the Android App
[AwesomeApp](https://github.com/cuplv/AwesomeApp) at commit
`04f68b69a6f9fa254661b481a757fa1c834b52e1`.
[AwesomeApp.zip](../test/data/AwesomeApp.zip) already contains the app
content and the related build artifact and is an example of repository
we expect to analyze with the `biggroumcheck.sh` script.

We tested directly the `biggroumcheck.sh` script with the following
test cases.

The test (and in practice only the test for `finalize`)  requires to
set the `filepath` passed tp the script to the path **containing** the
Android App.

We tested each command of `biggroumcheck.sh` as follows:

```bash
`biggroumcheck.sh <path_containing_awesome_app> 04f68b69a6f9fa254661b481a757fa1c834b52e1 <command>
```

providing one of the available values for `<command>` and the following inputs (via stdin):

- applicable:
  - stdin: [example_applicable_input.json](./musedev_integration_tests/example_applicable_input.json)
  - expected stdout: [expected_applicable_output.json](./musedev_integration_tests/expected_applicable_output.json)

- version
  - stdin: [example_version_input.json](./musedev_integration_tests/example_version_input.json)
  - expected stdout: [expected_version_output.json](./musedev_integration_tests/expected_version_output.json)

- run
  - stdin: [example_run_input.json](./musedev_integration_tests/example_run_input.json)
  - expected stdout: [example_run_output.json](./musedev_integration_tests/example_run_output.json)

- finalize
  - stdin: [example_finalize_input.json](./musedev_integration_tests/example_finalize_input.json)
  - expected stdout: [example_finalize_output.json](./musedev_integration_tests/example_finalize_output.json)

- talk (**TODO** Missing)
  - stdin: [example_talk_input.json](./musedev_integration_tests/example_talk_input.json)
  - expected stdout: [example_talk_output.json](./musedev_integration_tests/example_talk_output.json)

- reaction (**TODO** Missing)
  - stdin: [example_reaction_input.json](./musedev_integration_tests/example_reaction_input.json)
  - expected stdout: [example_reaction_output.json](./musedev_integration_tests/example_reaction_output.json)

The script returns the content of `expected stdout` on the standard output when invoked with the provided input.



## Testing the API on your local machine

We describe how you can run and test the API **locally** (i.e., you
will spin up the BigGroum search service and directly invoke the
`biggroumcheck.sh` script on the analyst Docker container).

As a pre-requisite, clone the BigGroum repository:
```bash
git clone https://github.com/cuplv/biggroum.git
cd biggroum
git checkout develop
git submodule update --init --recursive --remote
```

### Running the Automatic Integration Tests
The script [start_and_test_docker.sh](musedev_integration_tests
./start_and_test_docker.sh) automatically tests the BigGroum MuseDev
API using docker containers:
```
cd biggroum/python/fixrgraph/musedev/musedev_integration_tests
./start_and_test_docker.sh
```

The script automatically downloads (from DockerHub) the docker images
and runs the docker containers required to test the API. The script
then runs the two docker containers implementing the BigGroum
search services and the musedev analyst docker container (you need to
have access to the analyst image to run this test). Finally, the
script runs the test cases for the `version`, `applicable`, `run`, and
`finalize` commands.

The script takes about 2 minutes (probably more if you need to
download the images from DockerHub) to run as it installs the required
dependencies on the docker containers and runs the tests. 

The script will output each executed command, with its input, its
output, and the expected output.


### Running the API Manually

You can run the API manually following these steps (use step 1 and 2
if you want to deploy a local version of the Fixr search service ---
otherwise go to step 3):

1) Generate the Docker compose file for the Fixr search and source code service (the following will use a small set of test data):

```
cd docker_compose
python get_docker_compose.py --remote -v latest -d
```

2) Start the search and source code service: service:
```
docker-compose up
```

3) Run the (musedev/analyst) docker container setting the `FIXR_SEARCH_ENDPOINT` environment variable to the deployment url of the Fixr search service (it should be `localhost` if you want to use the services you just started).

```
TODO: HOW?
```

4) Copy [biggroumcheck.sh](biggroumcheck.sh) into the docker container in `/root/biggroumcheck.sh`:

```
TODO: HOW?
```

5) Copy a built android application into the container.

You can use the Android app in the archive
[AwesomeApp.zip](../test/data/AwesomeApp.zip). You can extract it's
content in the `root` folder of the container.

```
TODO: HOW?
```


6) Call the `biggroumcheck.sh` script:
```
/root/biggroumcheck.sh /root/AwesomeApp $HASH $COMMAND
```

At this point, you should provide the residue input data from the
command line. You can use the input data we provided above in our test
cases for the `AwesomeApp` Android app.

The output data is returned via standard output.


### Note about the runtime
The biggroumcheck.sh script will install the necessary dependencies at
runtime (the isntallation of dependencies is specific for the analyst
container and will not work on other platforms).

For convenience, the installation step is skipped if the script has
been run previously in the same docker container.


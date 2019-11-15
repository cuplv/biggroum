#!/bin/bash

# Use:  In the .muse.toml specify:
# ```
# customTools = "https://raw.githubusercontent.com/cuplv/biggroum/master/python/fixrgraph/musedev/biggroumcheck.sh"
# ```
#
# to invoke the script: ./biggroumcheck.sh <filepath> <commit> <command>
# For example:
# echo '{ "residue" : {}, "cwd" : "", "cmd" : "", "args" : "", "classpath" : [],  "files" : ["file1.java", "file2.java"]}' | ./biggroumcheck.sh 1 2 run
#
dir=$1
commit=$2
cmd=$3
shift
shift
shift
echo "dir: ${dir}"
echo "commit: ${commit}"
echo "cmd: ${cmd}"


# perform initalization tasks
# - download the fixrgraph python package
# - set the PYTHONPATH directory
# - download the graph extractor
# - to pass to the biggroumscript.py (we could have a configuration file in the repository to set those params):
#   - the URL to the biggroum search service (must be passed to the biggroumscript somehow, e.g., as a new input parameter)
#   - the path to the graph extractor
#
if [[ ! -f /opt/setup_complete ]]
then
	source /opt/setup_docker.sh
fi



# Call the script invoking biggroum
cd "$( dirname "${BASH_SOURCE[0]}")"
python biggroumscript.py "${dir}" "${commit}" "${cmd}" < /dev/stdin 1> /dev/stdout 2> /dev/stderr
exit $?

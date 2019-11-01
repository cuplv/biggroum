""" Mock interface.
"""

import requests
import json
import sys
import logging

class CommandInput:
    def __init__(self, filepath, commit, command, outstream):
        self.filepath = filepath
        self.commit = commit
        self.command = command
        self.outstream = outstream

def applicable(command_input):
    print("Applicable")
    return 0

def version(command_input):
    print("version")
    return 0

def run(command_input):
    print("run")
    return 0

def finalize(command_input):
    print("finalize")
    return 0

def talk(command_input):
    print("talk")
    return 0

def reaction(command_input):
    print("reaction")
    return 0


# ./tool.sh <filepath> <commit> <command>
# python biggroumscript.sh <filepath> <commit> <command>
def main(input_args=None):

    def usage(msg=None):
        if (not msg is None):
            sys.stderr.write(msg)
            sys.stderr.write("\n")
        sys.stderr.write("Usage: python biggroumscript.sh <filepath> <commit> <command>\n")
        sys.stderr.flush()
        return 1

    if (len(input_args) != 4):
        return_code = usage()
    else:

        filepath = input_args[1]
        commit = input_args[2]
        command = input_args[3]

        cmds_map = {
            "applicable" : applicable,
            "version" : version,
            "run" : run,
            "finalize" : finalize,
            "talk" : talk,
            "reaction" : reaction,
        }

        if (command not in cmds_map):
            return_code = usage("%s is not a valid command" % command)
        else:
            cmd_input = CommandInput(filepath, commit, command, sys.stdout)
            return_code = cmds_map[command](cmd_input)

    sys.exit(return_code)


if __name__ == '__main__':
    main(sys.argv)

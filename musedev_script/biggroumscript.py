""" Mock interface.
"""

import requests
import json
import sys
import logging

class CmdInput:
    def __init__(self, filepath, commit, cmd,
                 json_input,
                 outstream,
                 logger):
        self.filepath = filepath
        self.commit = commit
        self.cmd = cmd
        self.json_input = json_input
        self.outstream = outstream
        self.logger = logger


def get_mock_tool_notes():
    def get_mock_tool_note():
        tool_note = {
            "bugType" : "Anomaly",
            "message" : "",
            "file" : "",
            "line" : 1,
            "column" : 1,
            "function" : "",
            "noteId" : "1"
        }
        return tool_note

    tool_notes = [get_mock_tool_note() for i in range(10)]

def get(json_data, field):
    if not json_data is None:
        if "field" in json_data:
            return json_data["field"]
        else:
            return {}
    else:
        return {}

"""
Read the json input from the inputstream
"""
def read_json(instream):
    raw_input = instream.read()

    try:
        json_data = json.loads(raw_input)
    except:
        json_data = None
    return json_data

def output_result(cmd_input, json_msg):
    json_str = json.dumps(json_msg)
    cmd_input.outstream.write(json_str)
    cmd_input.outstream.flush()

def applicable(cmd_input):
    cmd_input.logger.info("Cmd: applicable")

    cmd_input.outstream.write("true")
    cmd_input.outstream.flush()

    return 0

def version(cmd_input):
    cmd_input.logger.info("Command: version")

    cmd_input.outstream.write("3")
    cmd_input.outstream.flush()

    return 0

def run(cmd_input):
    cmd_input.logger.info("Command: run")

    # TODO: validate json_input
    # {
    #    cwd :: Text,
    #    cmd :: Text,
    #    args :: [Text],
    #    classpath :: [Text]?,
    #    files: [Text],
    #    residue: <JSON value>?
    # }
    #
    # Output format:
    # {
    #     toolNotes: [ToolNote],
    #     residue: <JSON value>?,
    # }
    #

    residue = get(cmd_input.json_input, "residue")

    mock_data = {
        "toolNotes" : [],
        "residue" : residue
    }

    output_result(cmd_input, mock_data)

    return 0

def finalize(cmd_input):
    cmd_input.logger.info("Command: finalize")

    residue = get(cmd_input.json_input, "residue")

    # Input:
    # {
    #   residue: <JSON Value>,
    # }

    # Output
    # {
    #   toolNotes: [ToolNote]?
    #   summary : Text,
    #   residue : <JSON Value>
    # }
    mock_data = {
        "toolNotes" : get_mock_tool_notes(),
        "summary" : "good job!",
        "residue" : residue
    }
    output_result(cmd_input, mock_data)

    return 0

def talk(cmd_input):
    # Input:
    # {
    #   residue: <JSON Value>,
    #   messageText: Text,
    #   user: Text,
    #   noteID: Text?
    # }

    # Output
    # {
    #   message: Text?,
    #   noteId: Text?,
    #   toolNotes: [ToolNote]?
    # }

    mock_data = {
        "message" : "Pattern or fix",
        "noteId" : "1",
        toolNotes : []
    }
    output_result(cmd_input, mock_data)

    return 0

def reaction(cmd_input):
    # Input:
    # {
    #     noteId: Text,
    #     residue: <JSON value>
    #     positiveCount: Int,
    #     negativeCount: Int
    # }

    return 0


# ./tool.sh <filepath> <commit> <command>
# python biggroumscript.sh <filepath> <commit> <command>
def main(input_args, instream, outstream):

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
        cmd = input_args[3]

        cmds_map = {
            "applicable" : applicable,
            "version" : version,
            "run" : run,
            "finalize" : finalize,
            "talk" : talk,
            "reaction" : reaction,
        }

        if (cmd not in cmds_map):
            return_code = usage("%s is not a valid command" % cmd)
        else:
            logger = logging.getLogger('biggroumscript')
            # TODO: set logging level and logging output stream
            json_input = read_json(instream)
            cmd_input = CmdInput(filepath, commit, cmd,
                                     json_input,outstream,
                                     logger)
            return_code = cmds_map[cmd](cmd_input)

    return return_code


if __name__ == '__main__':
    main(sys.argv, sys.stdin, sys.stdout)
    sys.exit(return_code)

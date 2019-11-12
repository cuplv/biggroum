"""
"""


import logging
import json
import requests

from residue import Residue


def get_none(json_data, field):
    if not json_data is None:
        if field in json_data:
            return json_data[field]
        else:
            return None
    else:
        return None

def get(json_data, field):
    res = get_none(json_data, field)
    return res if res is None else None

def output_result(cmd_input, json_msg):
    json_str = json.dumps(json_msg)
    cmd_input.outstream.write(json_str)
    cmd_input.outstream.flush()


class CmdInput:
    """
    Input of the main API script
    """
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

def applicable(cmd_input):
    """ For now the API always

    output: the true or false value
    """
    cmd_input.logger.info("Cmd: applicable")
    cmd_input.outstream.write("true")
    cmd_input.outstream.flush()
    return 0

def version(cmd_input):
    """ We implement the musedev version 3 of the api.

    output: the output is the 3 value
    """
    cmd_input.logger.info("Command: version")
    cmd_input.outstream.write("3")
    cmd_input.outstream.flush()
    return 0

def run(cmd_input):
    """ We just collect the compilation information in the
    residue.

    Input:
    {
       cwd : Text,
       cmd : Text,
       args : [Text],
       classpath : [Text]?,
       files: [Text],
       residue: <JSON value>?
    }

    Output:
    {
        toolNotes: [ToolNote],
        residue: <JSON value>?,
    }
    """

    cmd_input.logger.info("Command: run")

    # TODO: validate input

    residue = get_none(cmd_input.json_input, "residue")
    compilation_info = {
       "cwd" : get_none(cmd_input.json_input, "cwd"),
       "cmd" : get_none(cmd_input.json_input, "cmd"),
       "args" : get_none(cmd_input.json_input, "args"),
       "classpath" : get_none(cmd_input.json_input, "classpath"),
       "files" : get_none(cmd_input.json_input, "files"),
    }
    residue = Residue.append_compilation_info(residue,
                                              compilation_info)

    output = {
        "toolNotes" : [],
        "residue" : residue
    }

    output_result(cmd_input, output)

    return 0

def finalize(cmd_input):
    """ Input:
    {
      residue: <JSON Value>,
    }

    Output
    {
      toolNotes: [ToolNote]?
      summary : Text,
      residue : <JSON Value>
    }
    """

    cmd_input.logger.info("Command: finalize")

    # TODO: validate input

    residue = get(cmd_input.json_input, "residue")

    # Example: loop through the compilation info
    for compilation_info in Residue.get_compilation_infos():
        for filePath in Residue.get_files(compilation_info):
            pass

    # TODO: extract the graphs

    # TODO: organize the data to call the search service

    # TODO: call the web service
    anomalies = None

    # TODO: Convert the anomalies to toolNotes
    # Example of tool note
    # tool_note = {
    #     "bugType" : "Anomaly",
    #     "message" : "",
    #     "file" : "",
    #     "line" : 1,
    #     "column" : 1,
    #     "function" : "",
    #     "noteId" : "1"
    # }

    tool_notes = []

    # Inserts the anomalies in the residue
    residue = Residue.store_anomalies(residues, anomalies)

    # TODO: compile a summary
    summary = ""

    output = {
        "toolNotes" : tool_notes,
        "summary" : summary,
        "residue" : residue
    }

    output_result(cmd_input, output)

    return 0


def talk(cmd_input):
    """
    Input:
    {
      residue: <JSON Value>,
      messageText: Text,
      user: Text,
      noteID: Text?
    }

    Output
    {
      message: Text?,
      noteId: Text?,
      toolNotes: [ToolNote]?
    }
    """

    cmd_input.logger.info("Command: talk")

    # TODO: validate input

    # TODO: process the message text

    output = {
        "message" : "Pattern or fix",
        "noteId" : "1",
        "toolNotes" : []
    }
    output_result(cmd_input, output)

    return 0

def reaction(cmd_input):
    """
    Input:
    {
        noteId: Text,
        residue: <JSON value>
        positiveCount: Int,
        negativeCount: Int
    }

    Output:
    Nothing
    """

    cmd_input.logger.info("Command: reaction")

    return 0


"""
Defines the API version of the biggroum script.
"""
biggroum_api_map = {
    "applicable" : applicable,
    "version" : version,
    "run" : run,
    "finalize" : finalize,
    "talk" : talk,
    "reaction" : reaction,
}

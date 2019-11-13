"""
"""


import logging
import json
import requests
import fixrgraph.extraction.extract_single as extract_single
import os
import tempfile
import shutil
import sys
import subprocess





from fixrgraph.musedev.residue import Residue

def get_none(json_data, field):
    if not json_data is None:
        if field in json_data:
            return json_data[field]
        else:
            return None
    else:
        return None

def output_json(cmd_input, json_msg):
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

    output_json(cmd_input, output)

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

    residue = get_none(cmd_input.json_input, "residue")

    # Example: loop through the compilation info
    javafiles = []
    for compilation_info in Residue.get_compilation_infos(residue):
        for filePath in Residue.get_files(compilation_info):
            if filePath.endswith(".java"):
                javafiles.append(filePath)

    # extract the graphs
    extractor_jar = os.getenv("GRAPHEXTRACTOR")
    try:
        graphdir = tempfile.mkdtemp(".groum_test_extract_single")

        # To call directly, uncomment the following lines
        #TODO: get github org and repo name
        extract_single.extract_single_class_dir(repo = ["unkown","unknown",cmd_input.commit],
                                                out_dir=graphdir,
                                                extractor_jar=extractor_jar,
                                                path=cmd_input.filepath,
                                                filter=javafiles,
                                                logger=cmd_input.logger)
        raise Exception("Unimplemented, exception will be removed when implementation completed.")

        # TODO: organize the data to call the search service (call wireprotocol compress here)

        # TODO: call the web service
        anomalies = None

    finally:
        shutil.rmtree(graphdir)

    # TODO: Convert the anomalies to toolNotes
    tool_notes = []
    for anomaly in anomalies:
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
        #
        # WARNING: noteId must be set to anomaly.numeric_id here!
        # tool_note = TODO
        # tool_notes.append()
        pass

    # Inserts the anomalies in the residue
    for anomaly in anomalies:
        residue = Residue.store_anomaly(residue, anomaly, anomaly.numeric_id)

    # TODO: compile a summary
    summary = ""

    output = {
        "toolNotes" : tool_notes,
        "summary" : summary,
        "residue" : residue
    }

    output_json(cmd_input, output)

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

    # Process the message text
    # The "parsing" of messages is rudimentary for now
    # The format of commands we expect are:
    # biggroum inspect
    # biggroum pattern
    #
    residue = get_none(cmd_input.json_input, "residue")
    note_id = get_none(cmd_input.json_input, "noteID")
    message_text = get_none(cmd_input.json_input, "messageText")

    if (not residue is None):
        message_text_splitted = message_text.split()

    if (residue is None or message_text is None):
        output_json(cmd_input, {})
        return 1
    elif (len(message_text_splitted) < 1):
        # We don't know if we have to handle the message.
        output_json(cmd_input, {})
        return 0
    elif (message_text_splitted[0] == "biggroum"):
        if (len(message_text_splitted) != 2):
            # Not enough inputs
            output_json(cmd_input, {})
            return 1
        elif not (message_text_splitted[1] == "inspect" or
                  message_text_splitted[1] == "pattern"):
            # Wrong commands
            output_json(cmd_input, {})
            return 1
        elif note_id is None:
            # No note id
            output_json(cmd_input, {})
            return 1
        else:
            anomaly = Residue.retrieve_anomaly(residue, note_id)

            if anomaly is None:
                output_json(cmd_input, {})
                return 1
            else:
                # TODO: get the pattern or the fix from the stored anomaly
                output = {
                    "message" : "Pattern or fix",
                    "noteId" : note_id,
                    "toolNotes" : []
                }
                output_json(cmd_input, output)
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

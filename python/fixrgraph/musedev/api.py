""" Implement the MuseDev API.
"""

import logging
import json
import requests
import fixrgraph.extraction.extract_single as extract_single
import fixrgraph.wireprotocol.search_service_wire_protocol as wp
import os
import tempfile
import shutil
import sys
import subprocess
import re
from string import Template

from fixrgraph.musedev.residue import Residue


# Constants used to set free options in the CmdInput class
GRAPH_EXTRACTOR_PATH = "GRAPH_EXTRACTOR_PATH"
FIXR_SEARCH_ENDPOINT = "FIXR_SEARCH_PATH"

REMOTE_DEBUG = True
DEBUG_ENDPOINT = "http://192.12.243.76:8081/remote_debug"

GITHUB_MESSAGE = """
----------------
*${ERROR_DESCRIPTION}* in `${METHOD_NAME}`
<details>
<summary>Methods Involved</summary>

```java
${ANOMALY_METHODS}
```
</details>
<details>
<summary>Reference Pattern</summary>

```java\n
${PATTERN_CODE}
```
</details>

<details>
<summary>Suggested Patch</summary>

```java
${PATCH_CODE}
```
</details>"""

import requests
def send_dbginfo(msg):
    if not REMOTE_DEBUG:
        return

    try:
        r = requests.post(DEBUG_ENDPOINT,
                          json={'msg':msg})

    except Exception as e:
        # fail silently
        pass


def get_none(json_data, field):
    if not json_data is None:
        if field in json_data:
            return json_data[field]
        else:
            return None
    else:
        return None

def output_json(cmd_input, json_msg):
    send_dbginfo({"result" : json_msg})

    json_str = json.dumps(json_msg)
    cmd_input.outstream.write(json_str)
    cmd_input.outstream.flush()

class CmdInput:
    """
    Input of the main API script
    """
    def __init__(self, filepath, commit,
                 cmd, json_input, outstream,
                 logger, options):
        self.filepath = filepath
        self.commit = commit
        self.cmd = cmd
        self.json_input = json_input
        self.outstream = outstream
        self.logger = logger
        self.options = options

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
    cmd_input.logger.info("cmd_input: %s" % json.dumps(cmd_input.json_input))

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

def generate_message(anomaly):
    def get_or_default(json, key, default):
        if key in json:
            return str(json[key])
        else:
            return default

    template = Template(GITHUB_MESSAGE)

    if "pattern" in anomaly:
        anomalyText = anomaly["pattern"]
        anomalyMethods = set([f[:-1] for f in
                              re.findall("[A-Za-z][A-Za-z0-9]+\.[A-Za-z][A-Za-z0-9]+\(", anomalyText) if(len(f) > 0)])
        if anomalyMethods == "":
            anomalyMethods = "Unkown methods"

    new_message = template.substitute(
        {
            "ERROR_DESCRIPTION" : get_or_default(anomaly, "error",
                                                 "Unknown error").capitalize(),
            "METHOD_NAME" : get_or_default(anomaly, "methodName",
                                           "method not available"),
            "METHOD_LINE" : get_or_default(anomaly, "line", "unknown line"),
            "ANOMALY_METHODS" : "\n".join(anomalyMethods),
            "PATTERN_CODE" : get_or_default(anomaly, "pattern",
                                            "Pattern not available"),
            "PATCH_CODE" : get_or_default(anomaly, "patch",
                                          "Patch not available")
        }
    )

    return new_message

def is_only_whitespace(body):
    if(isinstance(body,str)):
        return body.strip() == ""
    else:
        return False

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
    cmd_input.logger.info("cmd_input: %s" % json.dumps(cmd_input.json_input))

    # TODO: validate input

    residue = get_none(cmd_input.json_input, "residue")

    extractor_jar_path = cmd_input.options[GRAPH_EXTRACTOR_PATH]
    if (not os.path.isfile(extractor_jar_path)):
        cmd_input.logger.error("Cannot find the graph extractor " +
                               "jar: %s" % extractor_jar_path)
        return 1

    search_endpoint = cmd_input.options[FIXR_SEARCH_ENDPOINT]

    # Example: loop through the compilation info
    javafiles = []
    for compilation_info in Residue.get_compilation_infos(residue):
        for filePath in Residue.get_files(compilation_info):
            if filePath.endswith(".java"):
                javafiles.append(filePath)

    # extract the graphs
    try:
        graphdir = tempfile.mkdtemp(".groum_test_extract_single")

        # To call directly, uncomment the following lines
        # TODO: get github org and repo name
        # extract_single.extract_single_class_dir(["notset","notset",
        #                                          cmd_input.commit],
        #                                         graphdir,
        #                                         extractor_jar_path,
        #                                         cmd_input.filepath,
        #                                         javafiles,
        #                                         None)
        apk_blacklist = ["MapboxAndroidDemo-china-debug-androidTest.apk",
                         "MapboxAndroidDemo-global-debug-androidTest.apk",
                         "MapboxAndroidDemo-china-debug.apk",
                         "SharedCode-debug-androidTest.apk",
                         "MapboxAndroidWearDemo-debug-androidTest.apk",
                         "MapboxAndroidWearDemo-debug.apk"]

        extract_single.extract_single_apk(["notset","notset", cmd_input.commit],
                                          graphdir,
                                          extractor_jar_path,
                                          cmd_input.filepath,
                                          javafiles,
                                          None,
                                          apk_blacklist)

        # Organize the data to call the search service
        # Copy source files to directory to zip
        sourcesdir = os.path.join(graphdir, "sources")
        os.mkdir(sourcesdir)
        for f in javafiles:
            shutil.copyfile(f,os.path.join(sourcesdir,f.split(os.sep)[-1]))

        # compress files to send
        zipfiles = {"graphs" : None, "sources" : None}
        for zipfile in zipfiles:
            graphs_zip_tempfile = os.path.join(graphdir, "%s.zip" %zipfile)
            zipfiles[zipfile] = graphs_zip_tempfile
            wp.compress(os.path.join(graphdir,zipfile), graphs_zip_tempfile)

        # call the web service
        req_result = wp.send_zips(search_endpoint,
                                  zipfiles["graphs"],zipfiles["sources"])

        if (req_result.status_code != 200):
            cmd_input.logger.error("Error invoking the service:")
            cmd_input.logger.error("Endpoint: %s" % search_endpoint)
            cmd_input.logger.error("Status Code: %i" % req_result.status_code)
            return 1

        response_data = [d for d in req_result.json() if ("patch" in d) and not is_only_whitespace(d["patch"])]
        tool_notes = []
        for anomaly in response_data:
            sourcefiles = extract_single.findFiles(cmd_input.filepath,"java")
            split = anomaly["className"].split(".")
            simpleClassName = split[-1] if len(split) > 1 else anomaly["className"]
            candidateFiles = [j.split(cmd_input.filepath)[-1] for j in sourcefiles if (simpleClassName in j) and extract_single.matchesPackage(j,anomaly["packageName"])]
            # Create a tool note for the anomaly
            candidate_file = candidateFiles[0] if len(candidateFiles) > 0 else "Failed to find File"
            if len(candidate_file) > 0 and candidate_file[0] == "/":
                candidate_file = candidate_file[1:]

            message = generate_message(anomaly)

            tool_note = {
                "type" : "BigGroum Anomaly",
                "message" : message,
                "file" : candidate_file,
                "line" : anomaly["line"],
                "column" : 0,
                "function" : anomaly["methodName"],
                "noteId" : anomaly["id"]
            }
            tool_notes.append(tool_note)

            # Insert the anomaly in the residue
            residue = Residue.store_anomaly(residue,
                                            anomaly,
                                            anomaly["id"])

        summary = "BigGroum found %d anomalies." % (len(tool_notes))

        output = {
            "toolNotes" : tool_notes,
            "summary" : summary,
            "residue" : residue
        }

        output_json(cmd_input, output)
    except Exception as e:
        cmd_input.logger.error(str(e))
        import traceback
        tb = traceback.format_exc()
        cmd_input.logger.error(tb)
        return 1
    finally:
        shutil.rmtree(graphdir)

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
                if message_text_splitted[1] == "inspect":
                    msg = anomaly["patch"]
                else:
                    msg = anomaly["pattern"]
                output = {
                    "message" : msg,
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

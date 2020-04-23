""" Python script implementing the musedev API 3
"""
import json
import sys
import logging

from fixrgraph.musedev.api import (
    GRAPH_EXTRACTOR_PATH,
    FIXR_SEARCH_ENDPOINT,
    CmdInput, biggroum_api_map,
    send_dbginfo
)

"""
Read the json input from the inputstream
"""
def read_json(instream, logger):
    raw_input = instream.read()

    # Empty input --- return empty json
    if raw_input.strip() == "":
        return {}

    try:
        json_data = json.loads(raw_input)
    except:
        json_data = None
        logger.error("Error reading input: %s" % raw_input)
        return None

    return json_data

def get_logger():
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    logger = logging.getLogger('biggroumscript')
    return logger

def main(input_args,
         instream,
         outstream,
         cmds_map,
         logger = None):

    if logger is None:
        logger = get_logger()

    logger.info("Calling main function with arguments: %s" % " ".join(input_args))

    def usage(msg=None):
        if (not msg is None):
            logger.error(msg)
            sys.stderr.write(msg)
            sys.stderr.write("\n")

        # python biggroumscript.sh <filepath> <commit> <command>
        #                          <graph_extractor_jar> <fixr_search_address>
        usage = "Usage: python biggroumscript.sh <filepath> <commit> <command>" \
                "<graph_extractor_jar> <fixr_search_address>\n"
        sys.stderr.write(usage)
        sys.stderr.flush()
        return 1

    if (len(input_args) != 6):
        return_code = usage("Wrong number of arguments")
    else:
        filepath = input_args[1]
        commit = input_args[2]
        cmd = input_args[3]
        graph_extractor_jar = input_args[4]
        fixr_search_endpoint = input_args[5]

        if (cmd not in cmds_map):
            return_code = usage("%s is not a valid command" % cmd)
        else:
            logger.info("About to execute cmd: %s" % cmd)
            json_input = read_json(instream, logger)
            if (json_input is None):
                return_code = 1
            else:
                cmd_input = CmdInput(filepath, commit, cmd,
                                     json_input,outstream,
                                     logger,
                                     options = {
                                         GRAPH_EXTRACTOR_PATH : graph_extractor_jar,
                                         FIXR_SEARCH_ENDPOINT : fixr_search_endpoint,
                                     })
                return_code = cmds_map[cmd](cmd_input)

    logger.info("Main function returns: %d" % return_code)

    return return_code


if __name__ == '__main__':
    logger = get_logger()

    msg = "Calling script with arguments: %s" % " ".join(sys.argv)
    logger.info(msg)
    send_dbginfo(msg)

    return_code = main(sys.argv,
                       sys.stdin,
                       sys.stdout,
                       biggroum_api_map,
                       get_logger())

    msg="Terminating script execution with %d" % return_code
    logger.info(msg)
    send_dbginfo(msg)

    sys.exit(return_code)

""" Python script implementing the musedev API 3
"""


import json
import sys
import logging

from api import CmdInput, biggroum_api_map

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

def get_logger():
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    logger = logging.getLogger('biggroumscript')
    return logger

# ./tool.sh <filepath> <commit> <command>
# python biggroumscript.sh <filepath> <commit> <command>
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

        usage = "Usage: python biggroumscript.sh <filepath> <commit> <command>\n"
        sys.stderr.write(usage)
        sys.stderr.flush()
        return 1

    if (len(input_args) != 4):
        return_code = usage("Wrong number of arguments")
    else:
        filepath = input_args[1]
        commit = input_args[2]
        cmd = input_args[3]

        if (cmd not in cmds_map):
            return_code = usage("%s is not a valid command" % cmd)
        else:
            logger.info("Command: reaction")

            # TODO: set logging level and logging output stream
            json_input = read_json(instream)
            cmd_input = CmdInput(filepath, commit, cmd,
                                 json_input,outstream,
                                 logger)
            return_code = cmds_map[cmd](cmd_input)

    logger.info("Main function returns: %d" % return_code)

    return return_code


if __name__ == '__main__':
    logger = get_logger()
    logger.info("Calling script with arguments: %s" % " ".join(sys.argv))

    return_code = main(sys.argv,
                       sys.stdin,
                       sys.stdout,
                       biggroum_api_map,
                       get_logger())

    logger.info("Terminating script execution with %d" % return_code)

    sys.exit(return_code)

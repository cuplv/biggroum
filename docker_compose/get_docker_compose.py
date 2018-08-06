""" Performs the runtime verification.
"""

import string
import sys
import os
import optparse
import logging


def _substitute(template, substitution):
    return string.Template(template).safe_substitute(substitution)


NEXUS_IP = "192.168.0.2"
NEXUS_PORT = "5005"
VERSION = "0.2"

LOCAL_IMAGES = {"SOLR_IMAGE" : "biggroum_solr",
                "SEARCH_IMAGE" : "biggroum_search",
                "SRC_IMAGE" : "srcfinder",
                "FRONTEND_IMAGE" : "biggroum_frontend"}

REP = (NEXUS_IP, NEXUS_PORT, VERSION)
REMOTE_IMAGES = {"SOLR_IMAGE" : "%s:%s/biggroum_solr:%s" % REP,
                 "SEARCH_IMAGE" : "%s:%s/biggroum_search:%s" % REP,
                 "SRC_IMAGE" : "%s:%s/srcfinder:%s" % REP,
                 "FRONTEND_IMAGE" : "%s:%s/biggroum_frontend:%s" % REP}

DOCKER_FILE = """version: '3'
services:
  biggroum_solr:
    image: ${SOLR_IMAGE}
    ports:
    - "30071:8983"
    hostname : biggroum_solr
    volumes:
    - ../FixrGraphPatternSearch/solr_groum:/persist

  biggroum_search:
    image: ${SEARCH_IMAGE}
    ports:
    - "30072:8081"
    links:
    - biggroum_solr
    hostname: biggroum_search
    volumes:
    - ../FixrGraphPatternSearch/sitevisit_extraction:/persist

  srcfinder:
    image: ${SRC_IMAGE}
    ports:
    - "30074:8080"
    hostname: srcfinder

  biggroum_frontend:
    image: ${FRONTEND_IMAGE}
    ports:
    - "30073:5000"
    links:
    - biggroum_search
    - srcfinder
    hostname: biggroum_frontend

"""

def main(input_args=None):
    p = optparse.OptionParser()

    p = optparse.OptionParser()

    p.add_option('-r', '--remote', action="store_true",
                 default=False,
                 help="Generate docker compose for the remote server")

    def usage(msg=""):
        if msg: print "----%s----\n" % msg
        p.print_help()
        sys.exit(1)

    if (input_args is None):
        input_args = sys.argv[1:]
    opts, args = p.parse_args(input_args)

    if (opts.remote):
        df = _substitute(DOCKER_FILE, REMOTE_IMAGES)
    else:
        df = _substitute(DOCKER_FILE, LOCAL_IMAGES)

    with open("docker-compose.yml", 'w') as outfile:
        outfile.write(df)
        outfile.close()

if __name__ == '__main__':
    main()

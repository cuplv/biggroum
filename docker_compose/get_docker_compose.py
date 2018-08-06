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
                "FRONTEND_IMAGE" : "biggroum_frontend",
                "SOLR_DATA_PREFIX" : "../FixrGraphPatternSearch",
                "SEARCH_DATA_PREFIX" : "../FixrGraphPatternSearch"}

REP = (NEXUS_IP, NEXUS_PORT)
REMOTE_IMAGES = {"SOLR_IMAGE" : "%s:%s/biggroum_solr:${VERSION}" % REP,
                 "SEARCH_IMAGE" : "%s:%s/biggroum_search:${VERSION}" % REP,
                 "SRC_IMAGE" : "%s:%s/srcfinder:${VERSION}" % REP,
                 "FRONTEND_IMAGE" : "%s:%s/biggroum_frontend:${VERSION}" % REP,
                 "SOLR_DATA_PREFIX" : "..",
                 "SEARCH_DATA_PREFIX" : ".."}

DOCKER_FILE = """version: '3'
services:
  biggroum_solr:
    image: ${SOLR_IMAGE}
    ports:
    - "30071:8983"
    hostname : biggroum_solr
    volumes:
    - ${SOLR_DATA_PREFIX}/solr_groum:/persist

  biggroum_search:
    image: ${SEARCH_IMAGE}
    ports:
    - "30072:8081"
    links:
    - biggroum_solr
    hostname: biggroum_search
    volumes:
    - ${SEARCH_DATA_PREFIX}/sitevisit_extraction:/persist

  srcfinder:
    image: ${SRC_IMAGE}
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

    p.add_option('-v', '--version',
                 help="Version number of the images")


    def usage(msg=""):
        if msg: print "----%s----\n" % msg
        p.print_help()
        sys.exit(1)

    if (input_args is None):
        input_args = sys.argv[1:]
    opts, args = p.parse_args(input_args)

    if (opts.remote):

        if (not opts.version):
            usage("You must provide a version "
                  "number to tag the images with the -v flag")

        remote_map = {}
        for key,value in REMOTE_IMAGES.iteritems():
            new_val = _substitute(value, {"VERSION" : opts.version})

            remote_map[key] = new_val

        df = _substitute(DOCKER_FILE, remote_map)


    else:
        df = _substitute(DOCKER_FILE, LOCAL_IMAGES)

    with open("docker-compose.yml", 'w') as outfile:
        outfile.write(df)
        outfile.close()

if __name__ == '__main__':
    main()

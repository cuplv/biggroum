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

LOCAL_IMAGES = {"SEARCH_IMAGE" : "biggroum_search",
                "SRC_IMAGE" : "srcfinder",
                "FRONTEND_IMAGE" : "biggroum_frontend",
                "SEARCH_DATA_PREFIX" : "../FixrGraphPatternSearch",
                "RESOURCES_BIGGROUM_SOLR" : "",
                "RESOURCES_BIGGROUM_SEARCH" : "",
                "RESOURCES_SRCFINDER" : "",
                "RESOURCES_BIGGROUM_FRONTEND" : ""}

REP = (NEXUS_IP, NEXUS_PORT)
REMOTE_IMAGES = {"SEARCH_IMAGE" : "%s:%s/biggroum_search:${VERSION}" % REP,
                 "SRC_IMAGE" : "%s:%s/srcfinder:${VERSION}" % REP,
                 "FRONTEND_IMAGE" : "%s:%s/biggroum_frontend:${VERSION}" % REP,
                 "SEARCH_DATA_PREFIX" : "/srv/col-search",
                 "RESOURCES_BIGGROUM_SEARCH" : """cpu_count: 8
    mem_limit: 8192000000
    network_mode: "bridge" """,
                 "RESOURCES_SRCFINDER" : """cpu_count: 4
    mem_limit: 4096000000
    network_mode: "bridge" """,
                 "RESOURCES_BIGGROUM_FRONTEND" : """cpu_count: 2
    mem_limit: 2048000000
    network_mode: "bridge" """}

DOCKER_FILE = """version: '2.2'
services:
  biggroum_search:
    image: ${SEARCH_IMAGE}
    ${RESOURCES_BIGGROUM_SEARCH}
    ports:
    - "30072:8081"
    links:
    hostname: biggroum_search
    volumes:
    - ${SEARCH_DATA_PREFIX}/demo_meeting:/persist

  srcfinder:
    image: ${SRC_IMAGE}
    ${RESOURCES_SRCFINDER}
    ports:
    - "30071:8080"
    hostname: srcfinder

  biggroum_frontend:
    image: ${FRONTEND_IMAGE}
    ${RESOURCES_BIGGROUM_FRONTEND}
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

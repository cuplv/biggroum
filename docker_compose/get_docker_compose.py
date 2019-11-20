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
                "SEARCH_DATA_PREFIX" : "../FixrGraphPatternSearch/fixrsearch/test/data",
                 "RESOURCES_BIGGROUM_SEARCH" : """cpu_count: 1
    mem_limit: 1024000000
    network_mode: bridge """,
                 "RESOURCES_SRCFINDER" : """cpu_count: 1
    mem_limit: 1024000000
    network_mode: bridge """}

TWOSIX_REP = "%s:%s" % (NEXUS_IP, NEXUS_PORT)

def get_remote_images(rep, use_test_data):
    search_data_prefix = LOCAL_IMAGES["SEARCH_DATA_PREFIX"] if use_test_data else "/srv/col-search"
    REMOTE_IMAGES = {"SEARCH_IMAGE" : "%s/biggroum_search:${VERSION}" % rep,
                     "SRC_IMAGE" : "%s/srcfinder:${VERSION}" % rep,
                     "FRONTEND_IMAGE" : "%s/biggroum_frontend:${VERSION}" % rep,
                     "SEARCH_DATA_PREFIX" : search_data_prefix,
                     "RESOURCES_BIGGROUM_SEARCH" : """cpu_count: 8
    mem_limit: 8192000000
    network_mode: bridge """,
                     "RESOURCES_SRCFINDER" : """cpu_count: 8
    mem_limit: 8192000000
    network_mode: bridge """}
    return REMOTE_IMAGES

DOCKER_FILE = """version: '2.2'
services:
  biggroum_search:
    image: ${SEARCH_IMAGE}
    ports:
    - "8081:8081"
    links:
    - srcfinder
    hostname: biggroum_search
    volumes:
    - ${SEARCH_DATA_PREFIX}:/persist
    ${RESOURCES_BIGGROUM_SEARCH}

  srcfinder:
    image: ${SRC_IMAGE}
    ports:
    - "8080:8080"
    hostname: srcfinder
    ${RESOURCES_SRCFINDER}
"""
def get_musedev_analyst(endpoint="http://biggroum_search:8081/process_muse_data"):
    #http://biggroum_search:8081/process_muse_data
    MUSEDEV_ANALYST = """  fixrgraph:
     environment:
     - FIXR_SEARCH_ENDPOINT=%s
     image: musedev/analyst
     hostname: fixrgraph_deploy
     command: ["sleep","9999999"]
     cpu_count: 1
     mem_limit: 1024000000
     network_mode: bridge
     links:
     - biggroum_search
    """ % endpoint
    return MUSEDEV_ANALYST
def main(input_args=None):
    p = optparse.OptionParser()

    p = optparse.OptionParser()

    p.add_option('-r', '--remote', action="store_true",
                 default=False,
                 help="Generate docker compose for the remote server")

    p.add_option('-v', '--version',
                 help="Version number of the images")
    p.add_option('-t', '--two_six', help="Pull images from private two six labs repo", action="store_true")
    p.add_option('-m', '--musedev_analyst', help="Start the musedev analyst", action="store_true")
    p.add_option('-d', '--use_test_data', help="attach test data to containers", action="store_true")


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
        rep = "cuplv" if not opts.two_six else TWO_SIX_REP

        for key,value in get_remote_images(rep, opts.use_test_data).iteritems():
            new_val = _substitute(value, {"VERSION" : opts.version})

            remote_map[key] = new_val
        
        
        df = _substitute(DOCKER_FILE, remote_map)
        if opts.musedev_analyst:
            df = df + get_musedev_analyst()

    else:
        df = _substitute(DOCKER_FILE, LOCAL_IMAGES)

    with open("docker-compose.yml", 'w') as outfile:
        outfile.write(df)
        outfile.close()

if __name__ == '__main__':
    main()

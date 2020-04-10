import requests
import json
import optparse
import sys
import logging
import httplib

def test_json(condition, reply, error_msg):
    if not condition:
        print("*** FAILURE!\n\t%s\n" % error_msg)

        logging.debug(reply)

        return False
    else:
        return True


def test_search(address, port):
    print("*** Testing biggroum_search service...")

    service_address = "%s:%s" % (address, port)

    user_name = "smover"
    repo_name = "AwesomeApp"
    commit_hash = "04f68b69a6f9fa254661b481a757fa1c834b52e1"
    commit_hash_data = {"data" : [{"sha" : commit_hash}]}
    pr_id = 1

    pull_request_data = {"user" : user_name,
                         "repo" : repo_name,
                         "commitHashes" : commit_hash_data,
                         "modifiedFiles" : [],
                         "pullRequestId" : pr_id}

    try:
        r = requests.post("http://%s/process_graphs_in_pull_request" % service_address,
                          json=pull_request_data)

    except requests.ConnectionError as e:
        print("Connection Error")
        print(str(e))
        return 1
    except requests.Timeout as e:
        print("Timeout Error")
        print(str(e))
        return 1
    except requests.RequestException as e:
        print("Request exception")
        print(str(e))
        return 1

    print(r.status_code)
    if not test_json(r.status_code == 200, r,
                     "Wrong http result code"): return 1

    json_data = r.json()

    assert (len(json_data) > 0)

    # Compare with the expected output
    expected_output = [
      {
        u'methodName': u'showDialog',
        u'packageName': u'fixr.plv.colorado.edu.awesomeapp',
        u'fileName': u'[MainActivity.java](https://github.com/smover/AwesomeApp/blob/04f68b69a6f9fa254661b481a757fa1c834b52e1/app/src/main/java/fixr/plv/colorado/edu/awesomeapp/MainActivity.java)',
        u'className': u'fixr.plv.colorado.edu.awesomeapp.MainActivity',
        u'error': u'missing method calls',
        u'line': 47,
        u'id': 1
      },
      {u'methodName': u'showDialog',
       u'packageName': u'fixr.plv.colorado.edu.awesomeapp',
       u'fileName': u'[MainActivity.java](https://github.com/smover/AwesomeApp/blob/04f68b69a6f9fa254661b481a757fa1c834b52e1/app/src/main/java/fixr/plv/colorado/edu/awesomeapp/MainActivity.java)',
       u'className': u'fixr.plv.colorado.edu.awesomeapp.MainActivity',
      u'error': u'missing method calls',
       u'line': 47,
       u'id': 2
      }
    ]

    print json.dumps(json_data, sort_keys=True)
    print json.dumps(expected_output, sort_keys=True)

    assert(json.dumps(json_data, sort_keys=True) ==
           json.dumps(expected_output, sort_keys=True))

    print("*** SUCCESS!\n")

    return 0



def test_src_query(address, port,
                   src_srv_address = "srcfinder",
                   src_srv_port = 8080):
    print("*** Testing web server -- get src code...")

    ws_address = "http://%s:%s/src" % (address, port)
    service_address = "http://%s:%s/src" % (src_srv_address,
                                            src_srv_port)

    print("Address: %s" % "*** Testing web server -- get src code...")

    user = "anyremote"
    repo = "anyremote-android-client"
    class_name =  "anyremote.client.android.TextScreen"
    method = "commandAction"
    gitHubUrl = "https://github.com/%s/%s" % (user, repo)

    src_query = {
      "githubUrl" : gitHubUrl,
      "commitId" : "bc762d918fc38903daa55eaa8e481cd9c12b5bd9",
      "declaringFile" : "TextScreen.java",
      "methodLine" : 213,
      "methodName" : method,
      "url" : service_address
    }

    try:
        r = requests.post(ws_address,
                          json=src_query)


    except requests.ConnectionError as e:
        print("Connection Error")
        print(str(e))
        return 1
    except requests.Timeout as e:
        print("Timeout Error")
        print(str(e))
        return 1
    except requests.RequestException as e:
        print("Request exception")
        print(str(e))
        return 1

    if not test_json(r.status_code == 200, r,
                     "Wrong http result code"): return 1

    json_data = r.json()

    if not test_json(u"res" in json_data, r,
                     "No results in reply"):
        return 1
    if not test_json(len(json_data[u"res"]) == 2, r,
                     "Wrong results in reply"):
        return 1
    if not test_json(json_data[u"res"][0] == 214, r,
                     "Wrong return line"):
        return 1

    print("*** SUCCESS!\n")
    return 0

def main(input_args=None):

    p = optparse.OptionParser()
    p.add_option('-a', '--address', help="Ip address of the server")
    p.add_option('-p', '--search_port', help="Port of the search server")
    p.add_option('-w', '--srcsrv_port', help="Port of the src server")
    p.add_option('-d', '--debug', action="store_true",
                 default=False,
                 help="Print debug info")

    opts, args = p.parse_args()
    def usage(msg=""):
        if msg: print("----%s----\n" % msg)
        sys.exit(1)

    to_check = [(opts.address,
                 "Server address not provided! (try 100.120.0.6)"),
                (opts.search_port,
                 "Search port not provided! (try 30072)"),
                (opts.srcsrv_port,
                 "Source port port not provided! (try 30071)")]

    if (opts.debug):
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger(__name__).info("Enabling debug...")

        old_send= httplib.HTTPConnection.send
        def new_send(self, data):
            logger = logging.getLogger(__name__)
            logger.debug(data)
            return old_send(self, data)
        httplib.HTTPConnection.send= new_send
    else:
        logging.basicConfig(level=logging.INFO)


    for (opt_val, msg) in to_check:
        if (not opt_val):
            usage(msg)

    test_search(opts.address, opts.search_port)
    test_src_query(opts.address, opts.srcsrv_port)

if __name__ == '__main__':
    main()

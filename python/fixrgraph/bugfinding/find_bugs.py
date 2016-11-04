# Mockup tool to find bugs using the isomorphism computation and
# community detection.
#
# Now the tool do not use the community graph and outputs a set of
# fixed results for each app.
#

import sys
import os
import stat
import optparse
import logging
import traceback
import shutil
import json
import subprocess
import re
import traceback
import string

from fixrgraph.extraction.run_extractor import RepoProcessor


# TODO: share code with the extraction script
MIN_HEAP_SIZE="1024m"
MAX_HEAP_SIZE="4096m"
TIMEOUT="60"


single_res = \
"""<!DOCTYPE html>
<html>

<script src="https://github.com/mdaines/viz.js/releases/download/v1.3.0/viz.js"></script>

<script>
var isoReq = new XMLHttpRequest();
isoReq.open('GET', './${DOTFILE}', true);
isoReq.send();
isoReq.onload = function() {
  var isoText = isoReq.responseText;
  var isoContainer = document.getElementById('iso');
  var iso = Viz(isoText, options={ format: 'svg', engine: 'dot' });
  isoContainer.innerHTML = iso;
};

var isoReqFix = new XMLHttpRequest();
isoReqFix.open('GET', './${DOTFILE_FIX}', true);
isoReqFix.send();
isoReqFix.onload = function() {
  var isoTextFix = isoReqFix.responseText;
  var isoContainerFix = document.getElementById('isofix');
  var iso = Viz(isoText, options={ format: 'svg', engine: 'dot' });
  isoContainerFix.innerHTML = isofix;
};

</script>

<title>Bugs in the method ${METHOD_NAME}</title>

<body>

<h1>Example of output</h1>

<div style="float:left; width:50%;">
<h1>Bug</h1>
<p>Repository: <a href="${REPO_URL}">${USER_NAME}/${REPO_NAME}/${HASH}</a>
</p>
<p>File (line: ${LINE_NUMBER}): ${FILE_NAME}<a href="${REPO_URL}"> (Find)</a></p>
<p>Package: ${CLASS_PACKAGE}</p>
<p>Class: ${CLASS_NAME}</p>
<p>Method: ${METHOD_NAME}</p>

<h2 id="iso"></h2>

</div>

<div style="float:left; width:50%;">
<h2>Correct usage</h2>
<p>Repository: <a href="${REPO_URL_FIX}">${USER_NAME_FIX}/${REPO_NAME_FIX}/${HASH_FIX}</a>
</p>
<p>File (line: ${LINE_NUMBER_FIX}): ${FILE_NAME_FIX}<a href="${REPO_URL_FIX}"> (Find)</a></p>
<p>Package: ${CLASS_PACKAGE_FIX}</p>
<p>Class: ${CLASS_NAME_FIX}</p>
<p>Method: ${METHOD_NAME_FIX}</p>

<h2 id="isofix"></h2>

</div>

</body>
</html>
"""


all_res = \
"""<!DOCTYPE html>
<html>
<title>List of bugs</title>
<body>

<h1>Example of output</h1>

<table>

<tr>
<th>User</th>
<th>Repo</th>
<th>hash</th>
<th>Class name</th>
<th>Method Name</th>
<th>Line number</th>
</tr>

${ROWS}
</table>

</body>
</html>
"""

row_template = \
"""
<td>${USER_NAME}</td>
<td>${REPO_NAME}</td>
<td>${HASH}</td>
<td>${CLASS_NAME}</td>
<td><a href="${HTML}">${METHOD_NAME}</a></td>
<td>${LINE_NUMBER}</td>
</tr>
"""

def _substitute(template, substitution):
    return string.Template(template).safe_substitute(substitution)


def main():
    # Inputs
    #   - output for the result
    #   - input_path
    #   - repository info

    p = optparse.OptionParser()

    p.add_option('-i', '--indir', help="Base directory for the repo")
    p.add_option('-r', '--repo', help="Repo information (username:repo_name:hash)")
    p.add_option('-o', '--outdir', help="Output directory")

    # Extractor options
    p.add_option('-j', '--extractorjar', help="Jar file of the extractor (it must contain ALL the dependencies)")
    p.add_option('-l', '--classpath', help="Comma separated classpath used by the extractor - (i.e. add the android jar here)")

    def usage(msg=""):
        if msg: print "----%s----\n" % msg
        p.print_help()
        sys.exit(1)
    opts, args = p.parse_args()

    if (not opts.repo): usage("Missing repo")
    repo = opts.repo.split(":")
    if (len(repo) != 3): usage("Wrong repo format (%s)" % opts.repo)

    if (not opts.indir): usage("Missing indir!")
    if (not os.path.exists(opts.indir)): usage("%s does not exist!" % opts.indir)
    in_dir = opts.indir

    if (not opts.outdir): usage("Missing outdir!")
    if (os.path.exists(opts.outdir)): usage("%s already exists!" % opts.outdir)
    out_dir = opts.outdir

    if (not opts.extractorjar): usage("Missing extractor jar")
    if (not os.path.exists(opts.extractorjar)): usage("%s does not exist!" % opts.extractorjar)
    extractor_jar = opts.extractorjar

    if None != opts.classpath:
        for jarfile in opts.classpath.split(":"):
            if not os.path.exists(jarfile):
                usage("The jar file %s specified in the classpath does not exists!" % jarfile)
    classpath = opts.classpath

    if 'ANDROID_HOME' not in os.environ:
        raise Exception("ANDROID_HOME path is not set")
    else:
        android_home = os.environ['ANDROID_HOME']

    os.mkdir(out_dir)
    graph_dir = os.path.join(out_dir, "graphs")
    prov_dir = os.path.join(out_dir, "provenance")
    bugs_dir = os.path.join(out_dir, "bugs")
    os.mkdir(bugs_dir)

    # generate the graphs for the input app
    RepoProcessor.extract_static(repo,
                                 None,
                                 in_dir,
                                 android_home,
                                 graph_dir,
                                 prov_dir,
                                 classpath,
                                 extractor_jar)

    # Search for bugs using the community graphs
    #
    # STILL NOT IMPLEMENTED.
    # Most likely we will have a call to a web service where we pass
    # as input the generated ACDFG and we get results as output.
    #

    print ("\n*WARNING*\n" +
           "The tool now outputs a fix output for demonstration purposes!\n")

    # generate a fixed output

    # Generate a mockup output
    repo_url = "http://github.com/%s/%s/%s" % (repo[0],repo[1],repo[2])
    single_map = {"CLASS_NAME" : "ClassName",
                  "CLASS_PACKAGE" : "package",
                  "FILE_NAME" : "FileName.java",
                  "HASH" : repo[2],
                  "LINE_NUMBER" : "0",
                  "METHOD_NAME" : "methodName",
                  "REPO_NAME" : repo[1],
                  "REPO_URL" : repo_url,
                  "USER_NAME" : repo[0],
                  "CLASS_NAME_FIX" : "ClassName",
                  "CLASS_PACKAGE_FIX" : "package",
                  "FILE_NAME_FIX" : "FileName",
                  "HASH_FIX" : repo[2],
                  "LINE_NUMBER_FIX" : "0",
                  "METHOD_NAME_FIX" : "methodName",
                  "REPO_NAME_FIX" : repo[1],
                  "REPO_URL_FIX" : repo_url,
                  "USER_NAME_FIX" : repo[0]}
    bug_list = []
    for i in range(10): bug_list.append(single_map)

    # writes the single results
    rows = []
    i = 0
    for bug in bug_list:
        html_text = _substitute(single_res, bug)
        bug_file = os.path.join(bugs_dir, "bug_%d.html" % i)
        with open(bug_file, 'w') as fout:
            fout.write(html_text)
            fout.flush()
            fout.close()

        bug["HTML"] = bug_file
        row = _substitute(row_template, bug)
        rows.append(row)
        i = i + 1

    # write the output index
    bug_index = os.path.join(bugs_dir, "bug_index.html")
    all_res_html = _substitute(all_res, {"ROWS" : "\n".join(rows)})
    with open(bug_index, 'w') as fout:
        fout.write(all_res_html)
        fout.flush()
        fout.close()

    print ("\nSample output written in %s\n" % bug_index)



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    main()




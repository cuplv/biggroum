"""
createAnnotatedHTMLPage takes as inputs
 - The isomorphism
 - The two ACDFGs
 - The jimple file
 - It then annotates the isomorphism on the jimple file
 - Prints a HTML page that contains the annotated jimple files
   and other information such as the processed dot file.
"""
import sys
import acdfgClass
import jimpleClass
from cStringIO import StringIO
import logging

#import proto_iso
from protobuf.proto_iso_pb2 import Iso as ProtoIso

def get_iso_class(iso_pbuf_file):
    try:
        f = open(iso_pbuf_file, 'rb')
        pr_iso = ProtoIso()  # create a new acdfg
        pr_iso.ParseFromString(f.read())
        #pr_iso.parse_from_bytes(f.read())
        f.close()
        return pr_iso
    except IOError:
        logging.error('Could not read %s' % str(iso_pbuf_file))
        raise



class AnnotatedPageContent:

    def __init__ (self, acdfg_file_a, acdfg_file_b, jimple_file_a,  jimple_file_b, iso_file):
        # read all the components
        self.acdfg_a = acdfgClass.read_acdfg(acdfg_file_a)
        self.acdfg_b = acdfgClass.read_acdfg(acdfg_file_b)
        self.jimple_a = jimpleClass.read_jimple_file(jimple_file_a)
        self.jimple_b = jimpleClass.read_jimple_file(jimple_file_b)
        self.pr_iso = get_iso_class(iso_file)
        # Controlled through the logging library
        # To enable debug logging:
        # logging.basicConfig(level=logging.DEBUG)
        # self.debug = False

    def matchup_jimples(self):
        key_linenum_map_a = self.jimple_a.matchup_acdfg_nodes(self.acdfg_a)
        key_linenum_map_b = self.jimple_b.matchup_acdfg_nodes(self.acdfg_b)
        # Now use the iso and do a join
        self.jimple_a_to_b = {}
        self.jimple_b_to_a = {}
        # Iterate through all the node mappings in the pr_iso
        pr_iso = self.pr_iso
        for n_pair in pr_iso.map_node:
            key1 = int(n_pair.id_1)
            key2 = int(n_pair.id_2)
            if (key1 in key_linenum_map_a) and (key2 in key_linenum_map_b):
                logging.debug('Node keys: %s <---> %s' % (str(key1), str(key2)))
                line1 = key_linenum_map_a[key1]
                line2 = key_linenum_map_b[key2]
                self.jimple_a_to_b[line1] = line2
                self.jimple_b_to_a[line2] = line1
                logging.debug('Line numbers: %s <---> %s' % (str(line1), str(line2)))

    def get_javascript_dictionary(self):
        str = ''
        for (line1, line2) in self.jimple_a_to_b.items():
            str= str + '\"line__%d__a__\":\"line__%d__b__\",'%(line1, line2)
            str= str + '\"line__%d__b__\":\"line__%d__a__\",'%(line2, line1)
        return str

    def construct_template(self, dot_file_str):
        jscript_str = self.get_javascript_dictionary()
        templStr= """ <html> <body>
<!-- BEGIN added stylesheet -->
<style>
  .jimpleCode {
    font-family: \"PT Mono\", monospace;
  }
  .identi {
    display: none;
  }
  td {
    margin: 1em;
    font-size: .8em;
  }
  td span {
    font-size: 1.25em;
  }
  .iso_a {
    background: #fcc;
  }
  .iso_b {
    background: #ddf;
  }
  .iso_a.highlight {
    background: #f22;
    color: #fff;
  }
  .iso_b.highlight {
    background: #33f;
    color: #fff;
  }
  .highlight .identi {
    display: table-caption;
    background: #000;
    color: #fff;
    width: 1em;
    height: 1em;
    font-size: .8em;
    margin-left: 1em;
    padding: .2em;
    text-align: center;
    border-radius: 500px;
    font-weight: bold;
  }
</style>
<!-- END added stylesheet -->
<script>
var highlight_mapping = {
%s
};

/* Everything above untouched;
 * The rest of this is Rhys's
 */

var identiDict  = {};
var identiCount = 0;

function registerClick(event){
  if (!this.classList.contains("iso")) {
    return;
  }
  var lineName;
  var altLineName;
  for (className of this.classList) {
    if (className.substring(0, 4) == "line") {
      console.log("Line is " + className);
      lineName = className;
      break;
    }
  }
  altLineName = highlight_mapping[lineName];
  var alt = document.getElementsByClassName(altLineName)[0];
  this.classList.toggle("highlight");
  alt.classList.toggle("highlight");
}

document.addEventListener("DOMContentLoaded", function(event) {
  for (var element of document.querySelectorAll(".jimpleCode span")) {
    console.log(element.className);
    if (highlight_mapping[element.className]) {
      var identi = element.className;
      var identiElem = document.createElement('span');
      // numbering = highlight_mapping.indexOf(element.className);
      if (element.className[element.className.length - 3] == 'a') {
        element.className += " iso iso_a";
      }
      else {
        identi = highlight_mapping[element.className];
        element.className += " iso iso_b";
      }
      if (!identiDict[identi]) {
        identiCount += 1;
        identiDict[identi] = identiCount;
      }
      identi = identiDict[identi]
      identiElem.className = "identi"
      identiElem.innerHTML = identi;
      element.appendChild(identiElem);
      element.onclick = registerClick;
    }
  }
});
</script>
""" % (jscript_str)
        return templStr

    def print_jimple_to_string(self):
        """ Returns the head and body part of the generated html """
        head_str = self.construct_template('')

        str_list_a = self.jimple_a.to_html_str_list('a', self.jimple_a_to_b)
        str_list_b = self.jimple_b.to_html_str_list('b', self.jimple_b_to_a)

        body_stream = StringIO()

        body_stream.write('\n<table><tbody>\n')
        body_stream.write('<colgroup>\n')
        body_stream.write('<col width=\"50%\"/> <col width=\"50%\"/>\n')
        body_stream.write('</colgroup>\n')
        body_stream.write('<tr>\n')
        body_stream.write('<td> <span class=\"jimpleCode\">\n')
        body_stream.write('<table><tbody>\n')
        for hline in str_list_a:
            body_stream.write(hline)
        body_stream.write('</tbody></table>\n')
        body_stream.write('</span> </td>\n')
        body_stream.write('<td> <span class=\"jimpleCode\">\n')
        body_stream.write('<table><tbody>\n')
        for hline in str_list_b:
            body_stream.write(hline)
        body_stream.write('</tbody></table>\n')
        body_stream.write('</span> </td> </tr>\n')
        body_stream.write('</tbody></table>\n')
        return (head_str, body_stream.getvalue())

    def print_jimple_as_html(self, outfile_name):
        (head, body) = self.print_jimple_to_string()

        outfile = open(outfile_name,'w')
        outfile.write('<html> <body>\n')
        outfile.write(head)
        outfile.write(body)

        outfile.flush()
        outfile.close()


        # str_list_a = self.jimple_a.to_html_str_list('a', self.jimple_a_to_b)
        # str_list_b = self.jimple_b.to_html_str_list('b', self.jimple_b_to_a)
        # outfile.write('<html> <body>\n')
        # templStr = self.construct_template('')
        # outfile.write(templStr)
        # outfile.write('\n<table><tbody>\n')
        # outfile.write('<col width=\"50%\"> <col width=\"50%\">\n')
        # outfile.write('<tr>\n')
        # outfile.write('<td> <span class=\"jimpleCode\">\n')
        # outfile.write('<table><tbody>\n')
        # for hline in str_list_a:
        #     outfile.write(hline)
        # outfile.write('</table>\n')
        # outfile.write('</span> </td>\n')
        # outfile.write('<td> <span class=\"jimpleCode\">\n')
        # outfile.write('<table><tbody>\n')
        # for hline in str_list_b:
        #     outfile.write(hline)
        # outfile.write('</table>\n')
        # outfile.write('</span> </td>\n')
        # outfile.write('</table>\n')
        # outfile.write('</body>\n')
        # outfile.write('</html>\n')
        # outfile.close()





if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('Usage:', sys.argv[0], ' <file_with_file_names> ')
        sys.exit(1)
    info_file_name = sys.argv[1]
    try:
        info_file = open(info_file_name,'r')
        args_list=[]
        for line in info_file:
            line = line.strip()
            logging.debug(line)
            args_list.append(line)
        info_file.close()

    except IOError:
        msg = 'Could not open: %s' % info_file_name
        logging.error(msg)
        raise

    assert (len(args_list) >= 6)
    apc = AnnotatedPageContent(args_list[0], args_list[1], args_list[2], args_list[3], args_list[4])
    apc.matchup_jimples()
    apc.print_jimple_as_html(args_list[5])


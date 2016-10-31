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
import proto_iso

def get_iso_class(iso_pbuf_file):
    try:
        f = open(iso_pbuf_file, 'rb')
        pr_iso = proto_iso.Iso()  # create a new acdfg
        pr_iso.parse_from_bytes(f.read())
        f.close()
        return pr_iso
    except IOError:
        print('Could not read', iso_pbuf_file)
        raise
    


class AnnotatedPageContent:

    def __init__ (self, acdfg_file_a, acdfg_file_b, jimple_file_a,  jimple_file_b, iso_file):
        # read all the components
        self.acdfg_a = acdfgClass.read_acdfg(acdfg_file_a)
        self.acdfg_b = acdfgClass.read_acdfg(acdfg_file_b)
        self.jimple_a = jimpleClass.read_jimple_file(jimple_file_a)
        self.jimple_b = jimpleClass.read_jimple_file(jimple_file_b)
        self.pr_iso = get_iso_class(iso_file)
        self.debug = True

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
                print('Node keys:', key1 , '<--->', key2)
                line1 = key_linenum_map_a[key1]
                line2 = key_linenum_map_b[key2]
                self.jimple_a_to_b[line1] = line2
                self.jimple_b_to_a[line2] = line1
                if self.debug:
                    print('Line numbers: ', line1, ' <---> ', line2)

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
      element.append(identiElem);
      element.onclick = registerClick;
    }
  }
});
</script>
<!-- BEGIN code to load isomorphism -->
<script src="https://github.com/mdaines/viz.js/releases/download/v1.3.0/viz.js"></script>
<script>
var path_to_dot_file= \'%s\';
// ^ Sriram: you must specify this! It can be relative or absolute. --RBPO
var isoReq = new XMLHttpRequest();
isoReq.open('GET', path_to_dot_file, true);
isoReq.send();
isoReq.onload = function() {
  var isoText = isoReq.responseText;
  var isoContainer = document.getElementById('iso');
  var iso = Viz(isoText, options={ format: 'svg', engine: 'dot' });
  isoContainer.innerHTML = iso;
};
</script>
<!-- END code to load isomorphism -->
"""%(jscript_str,dot_file_str)
        return templStr
    
    def print_jimple_as_html(self, outfile_name):
        outfile = open(outfile_name,'w')
        str_list_a = self.jimple_a.to_html_str_list('a', self.jimple_a_to_b)
        str_list_b = self.jimple_b.to_html_str_list('b', self.jimple_b_to_a)
        print('<html> <body>', file = outfile)
        templStr = self.construct_template('')
        print(templStr, file=outfile)
        print('<table><tbody>', file = outfile)
        print('<col width=\"50%\"> <col width=\"50%\">', file = outfile)
        print('<tr>', file = outfile)
        print('<td> <span class=\"jimpleCode\">', file = outfile)
        print('<table><tbody>', file = outfile)
        for hline in str_list_a:
            print(hline, file = outfile)
        print('</table>' , file = outfile)
        print('</span> </td>' , file = outfile)
        print('<td> <span class=\"jimpleCode\">' , file = outfile)
        print('<table><tbody>', file = outfile)
        for hline in str_list_b:
            print(hline, file = outfile)
        print('</table>', file = outfile)
        print('</span> </td>', file = outfile)
        print('</table>', file = outfile)
        print('</body>', file = outfile)
        print('</html>', file = outfile)
        outfile.close()

    
        

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
            print(line)
            args_list.append(line)
        info_file.close()
        
    except IOError:
        print('Could not open:', info_file_name)
        raise
    
    assert (len(args_list) >= 6)
    apc = AnnotatedPageContent(args_list[0], args_list[1], args_list[2], args_list[3], args_list[4])
    apc.matchup_jimples()
    apc.print_jimple_as_html(args_list[5])
    

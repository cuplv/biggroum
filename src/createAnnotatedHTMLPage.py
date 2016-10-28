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

    def print_javascript_dictionary(self, outfile):
        print('<script>', file = outfile)
        print ('var highlight_mapping = { ', file = outfile)
        for (line1, line2) in self.jimple_a_to_b.items():
            print('\"line__%d__a__\":\"line__%d__b__\",'%(line1, line2), file = outfile)
            print('\"line__%d__b__\":\"line__%d__a__\",'%(line2, line1), file = outfile)
        print ('};', file = outfile)
        print("""
        function registerClick(span_id){
            if (highlight_mapping[span_id]){
                alt_span_id = highlight_mapping[span_id]
                var elem;
                if (document.getElementById) {
                    if (elem=document.getElementsByClassName(span_id)) {
                       if (elem[0].style) {
                           elem[0].style.backgroundColor=\"red\";
                       }
                     }
                     if (elem=document.getElementsByClassName(alt_span_id)) {
                       if (elem[0].style) {
                           elem[0].style.backgroundColor=\"yellow\";
                       }
                     }   
                }
            }
        }
        """, file=outfile)
        print('</script>', file=outfile)
        
        
    def print_jimple_as_html(self, outfile_name):
        outfile = open(outfile_name,'w')
        str_list_a = self.jimple_a.to_html_str_list('a', self.jimple_a_to_b)
        str_list_b = self.jimple_b.to_html_str_list('b', self.jimple_b_to_a)
        print('<html> <body>', file = outfile)
        self.print_javascript_dictionary(outfile)
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
    

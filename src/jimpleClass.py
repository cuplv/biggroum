"""
  Jimple Class: Load a jimple file and index the possible data and method nodes in the file.
"""
from __future__ import print_function
import sys
import string
import re
import acdfgClass



html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
}

def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)

class ParsePhaseEnum:
    decls = 1
    identities = 2
    stmts = 3



class Invoke:

    def __init__(self, linenum, call_type, class_name, fun_name, rcvr, res, args_str):
        self.call_type = call_type
        self.fun_name = fun_name
        self.rcvr = rcvr
        self.res = res
        args_str = args_str.strip()
        self.args_list=[]
        if len(args_str) > 0:
            self.args_list = args_str.split(',')
            self.args_list = [st.strip() for st in self.args_list]
        self.class_name = class_name
        self.line_num = linenum

    def get_line_num(self):
        return self.line_num

    def matchesMethodNode(self, mnode):
        assert isinstance(mnode, acdfgClass.MethodNode), ' Should be called with a method node'
        fname = self.class_name+'.'+self.fun_name
        if fname != mnode.get_name():
            print('Debug: match failed due to name mismatch: ', fname, mnode.get_name())
            return False
        
        print('Comparing arg list')
        # Now compare arguments list
        mnode_args = mnode.get_args()
        if len(mnode_args) != len(self.args_list):
            print('lengths differ', len(mnode_args), len(self.args_list))
            return False
        for anode in mnode_args:
            anode_name = anode.get_name()
            if anode_name != 'this' and anode_name not in self.args_list:
                print('argument: ', '('+anode_name+')', ' not found')
                return False
            
        return True
    
            

class JimpleObject:
    """ Load a Jimple program from a file and process it."""

    def __init__(self):
        self.file_lines = {} # each line of the file is annotated
        self.decl_idx = {}  # each declaration of a variable is annotated with the line
        self.invoke_idx = {} # each invoke is annotated and indexed by the method name and receiver
        self.phase = ParsePhaseEnum.decls
        self.file_name = ''
        self.debug = True
        self.invoke_re = re.compile('\s*([$ \w]*\s*=)?\s*(\w+)invoke\s*([$ \w]*\.)?<(.*):\s+(.*)\s+([ < > \w]+)\(.*\)>\((.*)\)\s*;')
        self.line_map={}

    def parse_line(self, count, line):
        # 1. What kind of a line is it?
        if ':=' in line:
            self.phase = ParsePhaseEnum.identities
            return  # no need to parse these for now
        else:
            if self.phase == ParsePhaseEnum.identities:
                self.phase = ParsePhaseEnum.stmts
        if '=' in line:
            self.phase = ParsePhaseEnum.stmts
        
        if self.phase == ParsePhaseEnum.decls:
            if len(line) > 0:
                if line[-1] == ';':
                    # Parse the declaration
                    # 1. split by ' '
                    line = line[0:-1]
                    wlst = line.split(' ')
                    decl_type = wlst[0].strip(' ,')
                    n_args = len(wlst)
                    for i in range(1, n_args):
                        arg = wlst[i].strip(' ,')
                        if arg == '':
                            continue
                        if arg in self.decl_idx:
                            print('Warning: @line', count, ' variable ', arg, ' already declared.')
                            lnum, typ = self.decl_idx[arg]
                            print('\t line number:', lnum, 'type: ', typ)
                        else:
                            self.decl_idx[arg] = (count, decl_type)
                            if self.debug:
                                print('D: @line', count, 'variable', '('+arg+')', 'declared with type:', decl_type)
        elif self.phase == ParsePhaseEnum.stmts:
            # Check for an invoke statement
            m = re.match(self.invoke_re, line)
            if m:
                res = m.group(1)
                if res:
                    res = res[0:-1]
                    res = res.strip()
                invoke_type = m.group(2)
                rcv = m.group(3)
                class_name = m.group(4)
                fun_name = m.group(6)
                args_list = m.group(7)
                if rcv:
                    rcv = rcv[0:-1] # remove the . at the end
                call_obj = Invoke(count, invoke_type, class_name, fun_name, rcv, res, args_list)
                fun_name = class_name + '.'+ fun_name
                if fun_name in self.invoke_idx:
                    lst = self.invoke_idx[fun_name]
                else:
                    lst = []
                    self.invoke_idx[fun_name] = lst
                if self.debug:
                    print('D: @line', count, 'call to function:', class_name+'.'+fun_name, ' receiver: ', rcv, ' result: ', res, ' arguments:' , args_list)
                lst.append(call_obj)



    def read_file(self, file_name):
        self.file_name = file_name
        try:
            self.phase = ParsePhaseEnum.decls
            f = open(file_name, 'r')
            count = 1
            for line in f:
                line = line.strip()
                self.file_lines[count] = line
                self.parse_line(count, line)
                self.line_map[count] = line
                count += 1
            self.num_lines = count
            f.close()

        except IOError:
            print('Fatal: error opening file', file_name)

    def to_html_str_list(self, stem, dict):
        line_template = string.Template('<tr><td> $line_num <td> <span class=\"$span_id\" style=\"background:$line_bg\" onClick=\"registerClick(\'$span_id\')\"> $line_string </span> </td></tr>')
        str_list = []
        for (lnum, line) in self.line_map.items():
            if lnum in dict:
                bgcolor='#ffbbbb'
            else:
                bgcolor='#ffffff'
                
            values = {'span_id':'line__'+str(lnum)+'__'+stem+'__',
                      'line_num': str(lnum),
                      'line_string': html_escape(line),
                      'line_bg':bgcolor}
            l_html = line_template.safe_substitute(values)
            str_list.append(l_html)
        return str_list
            
    def matchup_acdfg_nodes(self, acdfg):
        # Return a dictionary that maps key of data node in ACDFG to line number
        key_linenum_maps = {}
        # 1. Match up data nodes to possible declaration
        data_nodes = acdfg.get_data_nodes()
        for (key, data_node_obj) in data_nodes.items():
            d_name, d_type = data_node_obj.get_name() ,  data_node_obj.get_data_type()
            # Search for matching node and type
            if d_name in self.decl_idx:
                (count, decl_type) = self.decl_idx[d_name]
                #print('Data Node: ' , key , '('+d_name+')',' declaration in line : ', count, ' of type: ' , decl_type)
                key_linenum_maps[key] = count
            else:
                print('Data Node: ', key, '('+d_name+')', ' not found in jimple. ')
        
        # 2. Match up method nodes
        method_nodes = acdfg.get_method_nodes()
        for (key, meth_node_obj) in method_nodes.items():
            meth_node_name = meth_node_obj.get_name()
            print('Searcing for method:', meth_node_name)
            if meth_node_name in self.invoke_idx:
                lst = self.invoke_idx[meth_node_name]
                for inv in lst:
                    if inv.matchesMethodNode(meth_node_obj):
                        key_linenum_maps[key] = inv.get_line_num()
            if key not in key_linenum_maps:
                print('Method node:', key, '('+meth_node_name+')', 'Not found in jimple.')
        return key_linenum_maps

    


def read_jimple_file(file_name):
    j = JimpleObject()
    j.read_file(file_name)
    return j


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('Usage: ', sys.argv[0], ' <name of the jimple file> ')
        sys.exit(1)
    else:
        j = read_jimple_file(sys.argv[1])
        
    if len(sys.argv) >= 3:
        print('ACDFG file: ', sys.argv[2])
        acdfg = acdfgClass.read_acdfg(sys.argv[2])
        j.matchup_acdfg_nodes(acdfg)

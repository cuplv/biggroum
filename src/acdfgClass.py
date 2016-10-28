'''
Acdfg class will have the class definitions for loading
and creating acdfg objects
'''
from __future__ import print_function
from enum import Enum
import proto_acdfg


class NodeType(Enum):
    regular_node = 1
    data_node = 2
    method_node = 3


class EdgeType(Enum):
    control_edge = 1
    def_edge = 2
    use_edge = 3
    transitive_edge = 4
    exceptional_edge = 5
    


class Node:
    def __init__(self, node_type, key):
        self.node_type = node_type
        self.id = key
        assert isinstance(key, int)
        # assert isinstance(node_type, NodeType)

    # def __init__(self, key):
    #     self.node_type = NodeType.regular_node
    #     self.id = key
    #     assert isinstance(key, int)

    def get_type(self):
        return self.node_type

    def get_id(self):
        return self.id

    def get_node_type_str(self):
        if (self.node_type == NodeType.regular_node):
            return "regular node"
        elif (self.node_type == NodeType.data_node):
            return "data node"
        elif (self.node_type == NodeType.method_node):
            return "method node"
        else:
            assert False, ' Unhandled node type'


class DataNode(Node):
    def __init__(self, key, name, data_type):
        Node.__init__(self, NodeType.data_node, key)
        self.name = name
        self.data_type = data_type
        print('DataNode:',key, name, data_type)
        

    def get_name(self):
        return self.name

    def get_data_type(self):
        return self.data_type


class MethodNode(Node):
    def __init__(self, key, name, receiver, arg_list):
        Node.__init__(self, NodeType.method_node, key)
        self.name = name
        self.receiver = receiver
        self.arg_list = arg_list
        for a in arg_list:
            assert isinstance(a, DataNode)
        if receiver:
            assert isinstance(receiver, DataNode)
        assert isinstance(name, str)
        print('Method Node:', key, name)
    def get_name(self):
        return self.name

    def get_receiver(self):
        return self.receiver

    def get_args(self):
        return self.arg_list


class Edge:
    def __init__(self, edge_type, key, src, tgt):
        self.edge_type = edge_type
        self.id = key
        self.src = src
        self.tgt = tgt
        assert isinstance(src, Node)
        assert isinstance(tgt, Node)

    def get_id(self):
        return self.id

    def get_edge_type(self):
        return self.edge_type


class DefEdge(Edge):
    def __init__(self, key, src, tgt):
        Edge.__init__(self, EdgeType.def_edge, key, src, tgt)
        assert isinstance(tgt, DataNode)


class UseEdge(Edge):
    def __init__(self, key, src, tgt):
        Edge.__init__(self, EdgeType.use_edge, key, src, tgt)
        assert isinstance(src, DataNode)
        


class ControlEdge(Edge):
    def __init__(self, key, src, tgt):
        Edge.__init__(self, EdgeType.control_edge, key, src, tgt)


class TransitiveEdge(Edge):
    def __init__(self, key, src, tgt):
        Edge.__init__(self, EdgeType.transitive_edge, key, src, tgt)

class ExceptionEdge(Edge):
    def __init__(self, key, src, tgt):
        Edge.__init__(self, EdgeType.exceptional_edge, key, src, tgt)

class Acdfg:
    def __init__(self, acdfg_protobuf_obj):
        self.acdfg_protobuf = acdfg_protobuf_obj
        self.all_nodes = {}
        self.data_nodes = {}
        self.method_nodes = {}
        self.regular_nodes = {}
        self.all_edges = {}

    def add_node(self, node):
        assert isinstance(node, Node), \
            'Only node objects can be added through add_node'
        key = node.get_id()
        assert key not in self.all_nodes, \
            'key %d for node already present'%key
        self.all_nodes[key] = node
        if isinstance(node, DataNode):
            self.data_nodes[key] = node
        elif isinstance(node, MethodNode):
            self.method_nodes[key] = node
        else:
            self.regular_nodes[key] = node

    def get_data_nodes(self):
        return self.data_nodes

    def get_method_nodes(self):
        return self.method_nodes
    
    def add_edge(self, edge):
        assert isinstance(edge, Edge)
        key = edge.get_id()
        assert key not in self.all_edges, 'key %d for edge already present'%key
        self.all_edges[key] = edge

    def get_node_from_id(self, id):
        if id in self.data_nodes:
            return self.data_nodes[id]
        elif id in self.method_nodes:
            return self.method_nodes[id]
        elif id in self.regular_nodes:
            return self.regular_nodes[id]
        else:
            assert False, 'ID: %d not found'%(id)


def get_node_obj_from_ids(acdfg_obj, proto_edge):
    src = acdfg_obj.get_node_from_id(getattr(proto_edge, 'from'))
    tgt = acdfg_obj.get_node_from_id(proto_edge.to)
    return src, tgt


def read_acdfg(filename):
    try:
        f = open(filename, 'rb')
        acdfg = proto_acdfg.Acdfg()  # create a new acdfg
        acdfg.parse_from_bytes(f.read())
        acdfg_obj = Acdfg(acdfg)
        for dNode in acdfg.data_node:
            data_node_obj = DataNode(int ( getattr(dNode,'id') ) , dNode.name, getattr(dNode,'type'))
            acdfg_obj.add_node(data_node_obj)
        for mNode in acdfg.method_node:
            arg_ids = mNode.argument
            arg_list = [acdfg_obj.get_node_from_id(j) for j in arg_ids]
            if mNode.invokee:
                rcv = acdfg_obj.get_node_from_id(mNode.invokee)
            else:
                rcv = None
            method_node_obj = MethodNode(int(mNode.id), mNode.name, rcv, arg_list)
            acdfg_obj.add_node(method_node_obj)
        for rNode in acdfg.misc_node:
            misc_node_obj = Node(NodeType.regular_node,int(rNode.id))
            acdfg_obj.add_node(misc_node_obj)
        for ctrl_edge in acdfg.control_edge:
            src, tgt = get_node_obj_from_ids(acdfg_obj, ctrl_edge)
            cedge_obj = ControlEdge(ctrl_edge.id, src, tgt)
            acdfg_obj.add_edge(cedge_obj)
        for dedge in acdfg.def_edge:
            src, tgt = get_node_obj_from_ids(acdfg_obj, dedge)
            dedge_obj = ControlEdge(dedge.id, src, tgt)
            acdfg_obj.add_edge(dedge_obj)
        for uedge in acdfg.use_edge:
            src, tgt = get_node_obj_from_ids(acdfg_obj, uedge)
            uedge_obj = UseEdge(uedge.id, src, tgt)
            acdfg_obj.add_edge(uedge_obj)
        for tedge in acdfg.trans_edge:
            src, tgt = get_node_obj_from_ids(acdfg_obj, tedge)
            tedge_obj = TransitiveEdge(tedge.id, src, tgt)
            acdfg_obj.add_edge(tedge_obj)
        f.close()
        return acdfg_obj
    except IOError:
        print('Could not open: ', filename, 'for reading in binary mode.')
        assert False


        

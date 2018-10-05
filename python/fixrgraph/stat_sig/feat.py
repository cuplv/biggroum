"""
Extract the features used to define the null model from a graph
"""

import fixrgraph.annotator.protobuf.proto_acdfg_pb2

class Feat:
    METHOD_CALL = "method_call"
    METHOD_EDGE = "method_edge"

    def __init__(self, kind, desc):
        self.kind = kind
        self.desc = desc
        assert (kind in [self.METHOD_CALL, self.METHOD_EDGE])


class FeatExtractor:
    def __init__(self, graph_path):
        self.graph_path = graph_path

        with open(graph_path) as groum_file:
            self.proto_acdfg = proto_acdfg_pb2.Acdfg()
            self.proto_acdfg.ParseFromString(groum_file.read())
            groum_file.close()

        self.features = []
        self._extract_features()

    def features(self):
        """ Implement an iterator """
        raise NotImplementedError

    @static_method
    def _get_signature(method_node):
        if (method_node.HasField('assignee')):
            ret = "1"
        else:
            ret = "0"

        if (method_node.HasField('invokee')):
            invokee = "1"
        else:
            invokee = "0"

        if (method_node.HasField('argument')):
            args = len(method_node.argument)
        else:
            args = "0"

        signature = "%d_%d_%s_%d" % (ret,invokee,method_node.name,args)

        return signature

    def _extract_features(self):
        # Map from id to node
        idToNode = {}
        nodesLists = [self.proto_acdfg.method_node]
        for nodeList in nodesLists:
            for node in nodeList:
                idToNode[node.id] = node

        # Extract method set of method calls features
        for node in self.proto_acdfg.method_node:
            signature = FeatExtractor._get_signature(node)
            feat = Feat(Feat.METHOD_CALL, signature)
            self.features.append(feat)

        # Extract method edges features
        for edge in self.proto_acdfg.control_edge:
            # Just process method nodes
            if (edge.from in idToNode and
                edge.to in idToNode):

                src_node = idToNode[edge.from]
                dst_node = idToNode[edge.to]

                src_sig = FeatExtractor._get_signature(src_node)
                dst_sig = FeatExtractor._get_signature(dst_node)

                edge_sig = "%s -> %s" % (src_sig, dst_sig)

                feat = Feat(Feat.EDGE_SIG, edge_sig)
                self.features.append(feat)



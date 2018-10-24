"""
Extract the features used to define the null model from a graph
"""

from fixrgraph.annotator.protobuf.proto_acdfg_pb2 import Acdfg

class Feat:
    METHOD_CALL = "method_call"
    METHOD_EDGE = "method_edge"

    def __init__(self, kind, desc):
        self.kind = kind
        self.desc = desc
        assert (kind in [self.METHOD_CALL, self.METHOD_EDGE])

    def __repr__(self):
        return "%s - %s" % (self.kind, self.desc)

class FeatExtractor:
    def __init__(self, graph_path):
        self.graph_path = graph_path

        with open(graph_path) as groum_file:
            self.proto_acdfg = Acdfg()
            self.proto_acdfg.ParseFromString(groum_file.read())
            groum_file.close()

        self.graph_sig = FeatExtractor._get_graph_name(self.proto_acdfg)

        self.features = []
        self._extract_features()

    def get_features(self):
        """ Implement an iterator """
        return self.features

    def get_graph_sig(self):
        return self.graph_sig

    @staticmethod
    def _get_graph_name(proto_acdfg):
        graph_sig = ""
        if (proto_acdfg.HasField("repo_tag")):
            repoTag = proto_acdfg.repo_tag
            if (repoTag.HasField("user_name")):
                graph_sig += repoTag.user_name
            if (repoTag.HasField("repo_name")):
                graph_sig += repoTag.repo_name
            if (repoTag.HasField("url")):
                graph_sig += repoTag.url
            if (repoTag.HasField("commit_hash")):
                graph_sig += repoTag.commit_hash

        if (proto_acdfg.HasField("source_info")):
            protoSource = proto_acdfg.source_info

            if (protoSource.HasField("package_name")):
                graph_sig += protoSource.package_name
            if (protoSource.HasField("class_name")):
                graph_sig += protoSource.class_name
            if (protoSource.HasField("method_name")):
                graph_sig += protoSource.method_name
            if (protoSource.HasField("method_name")):
                graph_sig += protoSource.method_name

        return graph_sig

    @staticmethod
    def _get_method_signature(method_node):
        if (method_node.HasField('assignee')):
            ret = "1"
        else:
            ret = "0"

        if (method_node.HasField('invokee')):
            invokee = "1"
        else:
            invokee = "0"

        args = len(method_node.argument)

        signature = "%s_%s_%s_%d" % (ret,invokee,method_node.name,args)

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
            signature = FeatExtractor._get_method_signature(node)
            feat = Feat(Feat.METHOD_CALL, signature)
            self.features.append(feat)

        edges_list = [self.proto_acdfg.control_edge,
                      self.proto_acdfg.trans_edge]
        for edge_list in edges_list:
            # Extract method edges features
            for edge in edge_list:
                # Just process method nodes
                if (getattr(edge, 'from') in idToNode and
                    edge.to in idToNode):

                    src_node = idToNode[getattr(edge, 'from')]
                    dst_node = idToNode[edge.to]

                    src_sig = FeatExtractor._get_method_signature(src_node)
                    dst_sig = FeatExtractor._get_method_signature(dst_node)

                    edge_sig = "%s -> %s" % (src_sig, dst_sig)

                    feat = Feat(Feat.METHOD_EDGE, edge_sig)
                    self.features.append(feat)



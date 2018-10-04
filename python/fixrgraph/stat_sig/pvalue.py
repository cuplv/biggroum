"""
Compute the p-value for a graph

"""

import os
import sys
import functools
import operators
from fixrgraph.stat_sig.feat import FeatExtractor
from fixrgraph.stat_sig.db import FeatDb

def compute_p_value(graph_path,
                    address,
                    user,
                    password):
    featExtractor = FeatExtractor(graph_path)

    methodCalls = set()
    methodEdges = set()

    # Extract the features
    for feat in featExtractor.features():
        if feat.kind == FeatExtractor.METHOD_CALL:
            methodCalls.add(feat)
        elif feat.kind == FeatExtractor.METHOD_EDGE:
            methodEdges.add(feat)
        else:
            raise Exception("Unknown feature kind " + feat.kind)


    # Query the database
    featDb = FeatDb(address, user, password)
    featDb.open()

    # Compute the probability of the null model
    #
    # methodCalls = {m1, ..., mk}
    # methodEdges = {e1, ..., el}
    #
    # We compute P(e1 = 1, ..., el = 1) for the null model.
    #
    # We assume e1, ..., el to be independent. Then:
    # P(e1 = 1, ..., el = 1) = P(e1 = 1) ... P(el = 1)
    #
    # We compute P(ei = 1) as:
    # P(ei = 1) = P(ei=1, m1 = 1, ..., mk =1) / P(ei = 1)
    #
    methodEdgesProb = []
    for e in methodEdges:
        prob_all = featDb.count_features([e] + methodCalls)
        prob_e = featDb.count_feature([e])

        cond_prob = prob_all / prob_e
        methodEdgesProb.append(cond_prob)

    prob_graph = functools.reduce(operator.mul, methodEdgesProb, 1)

    return prob_graph


def main():
    p = optparse.OptionParser()
    p.add_option('-g', '--graph', help="Path to the groum file")

    p.add_option('-a', '--host', help="Address to the db server")
    p.add_option('-u', '--user', help="User to access the db")
    p.add_option('-p', '--password', help="Password to the db")

    def usage(msg=""):
        if msg:
            print "----%s----\n" % msg
        p.print_help()
        sys.exit(1)

    opts, args = p.parse_args()

    required = [opts.graph,opts.address,opts.user,opts.password]
    for r in required:
        if (not r):
            usage("Missing required argument!")
    if (not os.path.exists(opts.graph)): usage("Path %s does not exists!" % opts.graphs)


    pvalue = compute_p_value(opts.graphs,
                             opts.address,
                             opts.user,
                             opts.password)

    print("P-Value for %s: %f" % (opts.graph, pvalue))


if __name__ == '__main__':
    main()


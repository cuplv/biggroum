"""
Extract the graphs from a set of Android APKs and run the mining algorithms.


"""

from fixrgraph.pipeline.pipeline import Pipeline
from fixrgraph.test.TestPipeline import TestPipeline
import fixrgraph

import optparse
import shutil
import logging
import unittest
import sys
import os
import ConfigParser

def run_extraction(config):
    extractor_path = TestPipeline.get_extractor_path()
    fixrgraphiso_path = TestPipeline.get_fixrgraphiso_path()
    frequentsubgraphs_path = TestPipeline.get_frequentsubgraphs_path()
    gather_results_path = TestPipeline.get_gather_results_path()


    # Missing:
    # repo_list,
    # buildable_list,
    # build_data,
    # out_path
    out_path = os.path.join(config.get("extraction", "out_path"))
    extract_config = Pipeline.ExtractConfig(extractor_path,
                                            config.get("extraction", "repo_list"),
                                            config.get("extraction", "buildable_list"),
                                            config.get("extraction", "build_data"),
                                            out_path)

    groums_path = os.path.join(out_path, "graphs")
    cluster_path = os.path.join(out_path,"clusters")
    os.makedirs(cluster_path)
    cluster_file_path = os.path.join(cluster_path, "clusters.txt")
    groum_files_path = os.path.join(cluster_path, "groums_list.txt")

    TestPipeline.create_groums_file(groums_path, groum_files_path)
    itemset_config = Pipeline.ItemsetCompConfig(fixrgraphiso_path,
                                                config.get("itemset", "frequency_cutoff"),
                                                config.get("itemset", "min_methods_in_itemset"),
                                                groum_files_path,
                                                cluster_path,
                                                cluster_file_path)

    pattern_config = Pipeline.ComputePatternsConfig(groums_path,
                                                    cluster_path,
                                                    cluster_file_path,
                                                    config.get("pattern", "timeout"),
                                                    config.get("pattern", "frequency_cutoff"),
                                                    frequentsubgraphs_path)

    html_path = os.path.join(cluster_path, "html_files")
    # Missing: cluster number, to get automatically
    html_config = Pipeline.ComputeHtmlConfig(cluster_path,
                                             "1",
                                             gather_results_path)

    # Extract the graphs
    Pipeline.extractGraphs(extract_config)

    # Run the itemset computation
    Pipeline.computeItemsets(itemset_config)

    # Compute the patterns
    Pipeline.computePatterns(pattern_config)

    # Render the HTML results
    Pipeline.computeHtml(html_config)


def main():
    p = optparse.OptionParser()
    p.add_option('-c', '--configfile', help="Configuration file")
    opts, args = p.parse_args()

    def usage(msg=""):
        if msg:
            print "----%s----\n" % msg
        p.print_help()
        sys.exit(1)

    if (not opts.configfile): usage("No config file provided")
    if (not os.path.isfile(opts.configfile)):
        usage("%s is not a file" % opts.configfile)

    config = ConfigParser.RawConfigParser()
    config.read(opts.configfile)

    run_extraction(config)


if __name__ == '__main__':
    main()

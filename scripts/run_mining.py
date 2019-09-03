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

def get_default(config, section, option, default):
    try:
        val = config.get(section, option)
    except:
        val = default
    return val


def run_extraction(config):
    extractor_path = get_default(config, "extraction","extractor_jar",
                                 TestPipeline.get_extractor_path())
    fixrgraphiso_path = get_default(config, "itemset", "binary",
                                    TestPipeline.get_fixrgraphiso_path())
    frequentsubgraphs_path = get_default(config, "pattern", "binary",
                                         TestPipeline.get_frequentsubgraphs_path())
    gather_results_path = get_default(config, "html", "result_script",
                                      TestPipeline.get_gather_results_path())

    disable_extraction = False
    disable_itemset = False
    disable_pattern = False
    disable_html = False

    try:
        disable_extraction = config.getboolean("extraction","disabled")
    except:
        pass
    try:
        disable_itemset = config.getboolean("itemset","disabled")
    except:
        pass
    try:
        disable_pattern = config.getboolean("pattern","disabled")
    except:
        pass
    try:
        disable_html = config.getboolean("html","disabled")
    except:
        pass

    extract_config = None
    pattern_config = None
    itemset_config = None
    cluster_path = None
    cluster_file_path = None    

    out_path = os.path.join(config.get("extraction", "out_path"))
    groums_path = os.path.join(out_path, "graphs")

    if (not disable_extraction):
        try:
            tot_thread = int(config.getint("extraction","processes"))
        except:
            return 1

        extract_config = Pipeline.ExtractConfig(extractor_path,
                                                config.get("extraction", "repo_list"),
                                                config.get("extraction", "buildable_list"),
                                                config.get("extraction", "build_data"),
                                                out_path,
                                                tot_thread,
                                                config.getboolean("extraction", "use_apk"))

    if ((not disable_itemset) or (not disable_pattern) or (not disable_html)):
        cluster_path = os.path.join(out_path,"clusters")
        if (not os.path.isdir(cluster_path)):
            os.makedirs(cluster_path)
        cluster_file_path = os.path.join(cluster_path, "clusters.txt")


    if (not disable_itemset):
        print("Generating graphs list...")

        groum_files_path = os.path.join(cluster_path, "groums_list.txt")
        TestPipeline.create_groums_file(groums_path, groum_files_path, None)

        itemset_config = Pipeline.ItemsetCompConfig(fixrgraphiso_path,
                                                    config.get("itemset", "frequency_cutoff"),
                                                    config.get("itemset", "min_methods_in_itemset"),
                                                    groum_files_path,
                                                    cluster_path,
                                                    cluster_file_path)

    if (not disable_pattern):
        pattern_config = Pipeline.ComputePatternsConfig(groums_path,
                                                        cluster_path,
                                                        cluster_file_path,
                                                        config.get("pattern", "timeout"),
                                                        config.get("pattern", "frequency_cutoff"),
                                                        frequentsubgraphs_path)

    # Extract the graphs
    if (not disable_extraction):
        print("Extract groums...")
        assert not extract_config is None
        Pipeline.extractGraphs(extract_config)

    # Run the itemset computation
    if (not disable_itemset):
        print("Extract itemsets...")
        assert not itemset_config is None
        Pipeline.computeItemsets(itemset_config)

    # Compute the patterns
    if (not disable_pattern):
        print("Compute patterns...")
        assert not pattern_config is None
        Pipeline.computePatterns(pattern_config)

    # Render the HTML results
    if (not disable_html):
        print("Render HTML pages...")
        cluster_folders = os.path.join(cluster_path, "all_clusters")

        if (os.path.isdir(cluster_folders)):
            max_cluster = -1
            for path in os.listdir(cluster_folders):
                if path.startswith("cluster_"):
                    n_str = path[8:]
                    try:
                        n = int(n_str)
                        if n > max_cluster:
                            max_cluster = n
                    except:
                        pass


            try:
                genpng = config.getboolean("html", "genpng")
            except: 
                genpng = False

            html_config = Pipeline.ComputeHtmlConfig(cluster_path,
                                                     max_cluster,
                                                     gather_results_path,
                                                     genpng)
            Pipeline.computeHtml(html_config)

        else:
            print("The extraction did not find any pattern.")


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
    log_name = "extraction_log_" + str(os.getpid())
    logging.basicConfig(filename = log_name, level=logging.DEBUG)

    main()

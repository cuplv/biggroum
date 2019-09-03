""" High level script to compute the Groum patterns.
"""

from fixrgraph.extraction.run_extractor import RepoProcessor
from fixrgraph.clusters.clusters import Clusters

import logging
import os
import subprocess

""" Implements the graph extractor pipeline.

This should be the reference implementation to follow to port the
graph extraction to the bigglue pipeline.
"""

class Pipeline(object):

    """ Utility method used to call an external process
    """
    @staticmethod
    def _call_sub(args, cwd=None):
        # do not pipe stdout - processes will hang
        # we can pipe another stream
        proc = subprocess.Popen(args, cwd=cwd)
        proc.wait()

        return_code = proc.returncode
        if (return_code != 0):
            err_msg = "Error code is %s\nCommand line is: %s\n%s" % (str(return_code),
                                                                     str(" ".join(args)),"\n")
            logging.error("Error executing: %s\n" % (err_msg))
            return False
        return True



    """
    Configure the extraction process.

    The configuration contains the input of the extraction.
    """
    class ExtractConfig(object):
        # Prefix of the packages used to slice the graph
        default_slicing_filter = "android"
        default_step = "download"
        default_status_file = "extraction_status"

        """
        Input parameters for the extraction:
          - Path to the one-jar file of the graph extractor (https://github.com/cuplv/FixrGraphExtractor)
          - JSON file containing a list of input repositories
          - root path to the archive of built repositories (from the FixrBuilderService)
          - json file containing the list of built repositories (from the FixrBuildrService)
          - output path where the results and the logs are produced
        """
        def __init__(self,
                     graph_extractor_jar,
                     repo_list_file_path,
                     build_repo_list_file_path,
                     build_repo_path,
                     output_path,
                     tot_workers,
                     use_apk):
            self.graph_extractor_jar = graph_extractor_jar
            self.repo_list_file_path = repo_list_file_path
            self.build_repo_list_file_path = build_repo_list_file_path
            self.build_repo_path = build_repo_path
            self.output_path = output_path
            self.tot_workers = tot_workers
            self.use_apk = use_apk

    """
    Extract the graphs from the android projects.

    Input: see ExtractConfig
    Output:
      - creates the output directory config.output_path containing:
        - a graphs directory containing the binary format of the
          acdfgs (.acdfg.bin extension). The graphs are structured as
         user_name/repo_name/hash/<method_name>.bin.acdfg
        - a provenance directory containing the human readable
         representation of the extracted graphs (html and dot files
         for different graphs created for the process, like the cdfg,
         the sliced cdfg...)
    """
    @staticmethod
    def extractGraphs(config):
        # 1. Setup the output folder
        if not os.path.exists(config.output_path):
            os.makedirs(config.output_path)
        (indir, graphdir, provdir) = RepoProcessor.get_out_paths(config.output_path)
        extractor_status_file = os.path.join(graphdir,
                                             Pipeline.ExtractConfig.default_status_file)

        # 2. Perform the extraction
        repo_list = RepoProcessor.init_extraction(indir, graphdir,
                                                  provdir,
                                                  config.repo_list_file_path)
        repoProcessor = RepoProcessor(indir, graphdir, provdir,
                                      Pipeline.ExtractConfig.default_slicing_filter,
                                      config.graph_extractor_jar,
                                      None,
                                      config.build_repo_list_file_path,
                                      config.build_repo_path,
                                      extractor_status_file,
                                      config.tot_workers,
                                      config.use_apk)
        repoProcessor.processFromStep(repo_list,
                                      Pipeline.ExtractConfig.default_step)

    """
    Configuration for the itemset computation.

    - freqeunt_itemset_bin: absolute path to the executable that
      computes the frequent itemsets
    - frequency_cutoff: minimum frequency to consider an itemset frequent
    - min_methods_in_itemset: minimum number of methods in the itemset
    - groum_files_list: absolute path to the txt file containing a
      list of absolute paths to groums files
    - cluster_file: absolute path to the file containing the results
      of the itemset computation

    """
    class ItemsetCompConfig(object):
        def __init__(self,
                     frequent_itemset_bin,
                     frequency_cutoff,
                     min_methods_in_itemset,
                     groum_files_list,
                     cluster_path,
                     cluster_file):
            self.frequent_itemset_bin = frequent_itemset_bin
            self.frequency_cutoff = frequency_cutoff
            self.min_methods_in_itemset = min_methods_in_itemset

            self.groum_files_list = groum_files_list

            self.cluster_path = cluster_path
            self.cluster_file = cluster_file

    """ Compute the frequent itemset for a set of graphs.

    The input is a config object (it should be an ItemsetCompConfig)
    """
    @staticmethod
    def computeItemsets(config):
        # TODO: check if all the inputs are well formed
        must_exists = [config.frequent_itemset_bin,
                       config.groum_files_list]
        for f in must_exists:
            if not os.path.exists(f):
                raise IOError(f)

        args = [config.frequent_itemset_bin,
                "-f", str(config.frequency_cutoff),
                "-m", str(config.min_methods_in_itemset),
                "-o", config.cluster_file,
                config.groum_files_list]

        success = Pipeline._call_sub(args)

        if (not success):
            raise Exception("Error computing the frequent itemsets")

        # Creates the cluster directories
        Clusters.generate_graphiso_clusters(config.cluster_path,
                                            config.cluster_file)



    """
    Configuration for the computation of the patterns.
    """
    class ComputePatternsConfig(object):
        def __init__(self,
                     groums_path,
                     cluster_path,
                     cluster_file,
                     timeout,
                     frequency_cutoff,
                     frequentsubgraphs_path):
            self.groums_path = groums_path
            self.cluster_path = cluster_path
            self.cluster_file = cluster_file
            self.timeout = timeout
            self.frequency_cutoff = frequency_cutoff
            self.frequentsubgraphs_path = frequentsubgraphs_path

    """
    Run the computation of the of the cluster using make
    """
    @staticmethod
    def computePatterns(config):

        # Generate the makefile
        makefile_path = os.path.join(config.cluster_path, "makefile")
        Clusters.gen_make(config.cluster_path,
                          config.timeout,
                          config.frequency_cutoff,
                          config.groums_path,
                          config.frequentsubgraphs_path)

        # Run make
        args = ["make", "-f", makefile_path]
        success = Pipeline._call_sub(args)

        # if not success:
        #     raise Exception("Error computing the patterns")


    """
    Configuration for the computation of the html pages.
    """
    class ComputeHtmlConfig(object):
        def __init__(self,
                     cluster_path,
                     cluster_count,
                     gather_results_path,
                     gen_png=False):
            self.cluster_path = cluster_path
            self.cluster_count = cluster_count
            self.gather_results_path = gather_results_path
            self.gen_png = gen_png

    @staticmethod
    def computeHtml(config):
        html_files_path = os.path.join(config.cluster_path, "html_files")

        if (not os.path.exists(html_files_path)):
            os.mkdir(html_files_path)

        args = ["python",
                config.gather_results_path,
                "-a", "1",
                "-b", str(config.cluster_count),
                "-i", "all_clusters",
                "-o", "html_files"]

        success = Pipeline._call_sub(args, config.cluster_path)

        if not success:
            raise Exception("Error computing the html pages")

        if config.gen_png:

            for dotfile in os.listdir(html_files_path):
                if not dotfile.endswith(".dot"):
                    continue
                    
                basename = os.path.basename(dotfile)
                pngfile = "%s.png" % basename[:-4]
                
                args = ["dot",
                        "-Tpng",
                        "-o%s" % pngfile,
                        basename]

                success = Pipeline._call_sub(args, html_files_path)

                if not success:
                    logging.warning("Error computing the html pages "
                                    "for %s" % basename)






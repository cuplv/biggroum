""" High level script to compute the Groum patterns.
"""

from fixrgraph.extraction.run_extractor import RepoProcessor

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
                     output_path):
            self.graph_extractor_jar = graph_extractor_jar
            self.repo_list_file_path = repo_list_file_path
            self.build_repo_list_file_path = build_repo_list_file_path
            self.build_repo_path = build_repo_path
            self.output_path = output_path
    
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
        repo_list = RepoProcessor.init_extraction(indir, graphdir, provdir,
                                                  config.repo_list_file_path)
        repoProcessor = RepoProcessor(indir, graphdir, provdir,
                                      Pipeline.ExtractConfig.default_slicing_filter, 
                                      config.graph_extractor_jar,
                                      None,
                                      config.build_repo_list_file_path,
                                      config.build_repo_path,
                                      extractor_status_file)
        repoProcessor.processFromStep(repo_list,
                                      Pipeline.ExtractConfig.default_step)
        

    """
    Configure the itemset computation.

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
                     cluster_file):
            self.frequent_itemset_bin = frequent_itemset_bin
            self.frequency_cutoff = frequency_cutoff
            self.min_methods_in_itemset = min_methods_in_itemset
            self.groum_files_list = groum_files_list
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

        # The frequent itemset computation always return 1 as exit
        # code.
        # See: https://github.com/cuplv/FixrGraphIso/issues/13
        #
        # if (not success):
        #     raise Exception("Error computing the frequent itemsets")


    @staticmethod
    def computePatterns(config):
        raise NotImplementedError

    def computeHtmls(config):
        raise NotImplementedError


        


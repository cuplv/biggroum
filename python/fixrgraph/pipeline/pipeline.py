""" High level script to compute the Groum patterns.
"""

from fixrgraph.extraction.run_extractor import RepoProcessor

import logging
import os

""" Implements the graph extractor pipeline.

This should be the reference implementation to follow to port the
graph extraction to the bigglue pipeline.
"""

class Pipeline(object):
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
        


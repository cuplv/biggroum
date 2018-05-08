# Read the cluster_info files generated by the clusters
#

import re


class PatternInfo(object):
    def __init__(self, pattern_id, pattern_type, pattern_frequency,
                 groum_list, dot_filename):
        self.id = pattern_id
        self.type = pattern_type
        self.frequency = pattern_frequency
        self.groum_files_list = groum_list
        self.dot_name = dot_filename

class ClusterInfo(object):
    def __init__(self, cluster_id,
                 methods_list,
                 groum_list):
        self.id = cluster_id
        self.methods_list = methods_list
        self.groum_files_list = groum_list

def parse_cluster_info(cluster_info_stream):
    """ Parse the cluster_n_info.txt file to get a list of pattern info objects
    """
    patterns = []

    groum_list= []
    pattern_type = 1
    pattern_id = -1
    pattern_frequency = -1
    dot_filename = None

    match_bin = re.compile('(\w+)\s*Bin\s*#\s*(\d+)')
    match_dot = re.compile('Dot:\s*(.*.dot)')
    match_frequency_1 = re.compile('Frequency\s*:\s*(\d+),\s*(\d+)')
    match_frequency_2 = re.compile('Frequency\s*:\s*(\d+)(.*)$')
    match_groum = re.compile('(.*)\.acdfg\.bin')

    for line in cluster_info_stream:
        line = line.strip()

        m = match_bin.match(line)
        if m:
            if (pattern_id >= 0):
                pattern = PatternInfo(pattern_id,
                                      pattern_type,
                                      pattern_frequency,
                                      groum_list,
                                      dot_filename)
                patterns.append(pattern)

            groum_list= []
            pattern_type = 1
            pattern_id = -1
            pattern_frequency = -1
            dot_filename = None

            pattern_type = m.group(1).lower()
            pattern_id = m.group(2)
            continue

        m = match_dot.match(line)
        if m:
            dot_filename = m.group(1)
            continue


        m = match_frequency_1.match(line)
        if m:
            pattern_frequency = str(int(m.group(1)) + int(m.group(2)))
            continue

        # version with filename after frequency
        m = match_frequency_2.match(line)
        if m:
            pattern_frequency = m.group(1)
            groum_file_app = m.group(2)
            if "acdfg" in groum_file_app:
                groum_list.append(groum_file_app)
            continue

        m = match_groum.match(line)
        if m:
            if "Bin: " in line:
                continue
            groum_list.append(line)
            continue

    if (pattern_id >= 0):
        pattern = PatternInfo(pattern_id,
                              pattern_type,
                              pattern_frequency,
                              groum_list,
                              dot_filename)
        patterns.append(pattern)

    return patterns

def parse_clusters(cluster_file_stream):
    """ Parse the clusters.txt file to collect the list of clusters"""
    clusters_list = []

    cluster_id = 0
    methods_list = []
    groum_list = []

    match_cluster_start = re.compile('^I:\s*(.*)\(\s*\d+\s*\)$')
    match_cluster_file = re.compile('^F:\s*(.*)$')
    match_cluster_end = re.compile('^E\s*$')

    for line in cluster_file_stream:
        line = line.strip()

        m = match_cluster_start.match(line)
        if m:
            cluster_id += 1
            methods_list_str = m.group(1)
            methods_list_app = methods_list_str.split(",")
            methods_list = []
            for m in methods_list_app:
                methods_list.append(m.strip())
            continue

        m = match_cluster_file.match(line)
        if m:
            groum_list.append(m.group(1))
            continue

        m = match_cluster_end.match(line)
        if m:
            cluster = ClusterInfo(cluster_id,
                                  methods_list,
                                  groum_list)
            clusters_list.append(cluster)
            methods_list = []
            groum_list = []
            continue

    if (len(methods_list) != 0 or len(groum_list) != 0):
        raise Exception("The cluster file is truncated!")

    return clusters_list

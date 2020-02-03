#!/bin/python

""" Print a visualization of the lattice in html.

Start with building the DOT for the lattice.
"""

import sys
import logging
import os

import html

from string import Template
from fixrgraph.annotator.protobuf.proto_acdfg_pb2 import Acdfg
from fixrgraph.annotator.protobuf.proto_acdfg_bin_pb2 import Lattice
from collections import deque
import optparse
import subprocess

# Weird circular dependency, to fix
from fixrsearch.codegen.acdfg_repr import AcdfgRepr




DOT_ACDFGBIN_DOT="""${ID} [shape=box,style=filled,color="${COLOR}",label="${LABEL} ${FREQUENCY} ${POPULARITY}",href="${HREF}"];
"""

DOT_ACDFGBIN_DOT="""${ID} [shape=box,style=filled,color="${COLOR}",
label=<<table>
<tr><td href="${PROVENANCE_PATH}">${LABEL} ${FREQUENCY} ${POPULARITY} ${RELFREQ}</td></tr>
<tr><td href="${HREF}">pattern</td></tr>
</table>>];
"""

def _call_sub(args, cwd=None, env=None):
  # do not pipe stdout - processes will hang
  # we can pipe another stream
  if (env is None):
    proc = subprocess.Popen(args, cwd=cwd)
  else:
    proc = subprocess.Popen(args, cwd=cwd, env=env)
  proc.wait()

  return_code = proc.returncode
  if (return_code != 0):
    err_msg = "Error code is %s\nCommand line is: %s\n%s" % (str(return_code),
                                                                 str(" ".join(args)),"\n")
    logging.error("Error executing: %s\n" % (err_msg))
    return False
  return True


def check_eq(rel, non_trans):
  closure = set(non_trans)

  changed  = True
  while changed:
    to_add = set()
    for (a,b) in closure:
      for (c,d) in closure:
        if c == b and not (a,d) in closure:
          to_add.add((a,d))
    if len(to_add) > 0:
      closure.update(to_add)
    else:
      changed = False

  assert rel == closure


def get_node_color(acdfgBin):
  if (acdfgBin.popular):
    return "green"
  elif (acdfgBin.anomalous):
    return "red"
  elif (acdfgBin.isolated):
    return "yellow"
  else:
    return "grey"

def get_node_label(acdfgBin):
  return str(acdfgBin.id)

def printNodes(lattice, dot_stream, stats, f_filter, prefix_provenance):
  node_template = Template(DOT_ACDFGBIN_DOT)

  for acdfgBin in lattice.bins:
    if not f_filter(acdfgBin):
      continue

    (freq, pop, relfreq) = stats[acdfgBin.id]

    node_repr = node_template.substitute(
      {"ID" : str(acdfgBin.id),
       "COLOR" : get_node_color(acdfgBin),
       "LABEL" : get_node_label(acdfgBin),
       "FREQUENCY" : freq,
       "POPULARITY" : pop,
       "RELFREQ" : "%.2f" % relfreq,
       "PROVENANCE_PATH" : html.escape(get_repr_page(acdfgBin, prefix_provenance)),
       "HREF" : "%s.svg" % str(acdfgBin.id),
      })
    dot_stream.write(node_repr)


def get_stats(lattice, idToBin, trans_rel):
  """
  Get the popular measure exploring the lattice
  """

  def get_freq(acdfgBin):
    return len(acdfgBin.names_to_iso)

  idToStats = {}

  # Find the top nodes in the lattice
  to_visit = deque(lattice.bins)
  visited = set()
  total = 0
  while len(to_visit) > 0:
    acdfgBin = to_visit.pop()

    all_visited = True
    successors = []
    for (a, b) in trans_rel:
      if a == acdfgBin.id:
        all_visited = all_visited and b in visited
        successors.append(b)

    if all_visited:
      assert not acdfgBin.id in idToStats

      total += get_freq(acdfgBin)

      pop = get_freq(acdfgBin)
      while len(successors) > 0:
        nextId = successors.pop()
        nextBin = idToBin[nextId]
        pop += get_freq(nextBin)

        for (a, b) in trans_rel:
          if a == nextBin.id:
            successors.append(b)

      idToStats[acdfgBin.id] = [get_freq(acdfgBin), pop, 0]
      visited.add(acdfgBin.id)
    else:
      to_visit.appendleft(acdfgBin)


  for acdfgBin in lattice.bins:
    l = idToStats[acdfgBin.id]
    relfreq = (acdfgBin.cumulative_frequency * 1.0) / total
    idToStats[acdfgBin.id] = [get_freq(acdfgBin), acdfgBin.cumulative_frequency, relfreq]

  return idToStats

def get_rel(lattice):
  rel = set()
  for acdfgBin in lattice.bins:
    for incoming_id in acdfgBin.incoming_edges:
      rel.add((incoming_id, acdfgBin.id))
  return rel

def get_trans_rel(rel):
  new_rel = set(rel)
  changed = True
  while (changed):
    changed = False
    for (a,b) in rel:
      for (temp_b, c) in rel:
        if temp_b != b:
          continue
        for (temp_a, temp_c) in rel:
          if a == temp_a and c == temp_c:
            # (a,b) (b,c) (a,c)
            # delete (a,c), transitive edge
            if (a,c) in new_rel:
              new_rel.remove((a,c))
              changed = True

  check_eq(rel, new_rel)

  return new_rel


def create_dot_lattice(lattice, dot_stream,
                       prefix_provenance):
  """ Create the dot representation of the lattice
  """

  dot_stream.write("digraph lattice {\n")

  idToBin = {}
  for acdfgBin in lattice.bins:
    assert not acdfgBin.id in idToBin
    idToBin[acdfgBin.id] = acdfgBin

  rel = get_rel(lattice)
  trans_rel = get_trans_rel(rel)

  # Create nodes
  stats = get_stats(lattice, idToBin, trans_rel)

  printNodes(lattice, dot_stream, stats,
             lambda acdfgBin : acdfgBin.popular,
             prefix_provenance)
  printNodes(lattice, dot_stream, stats,
             lambda acdfgBin : acdfgBin.anomalous,
             prefix_provenance)
  printNodes(lattice, dot_stream, stats,
             lambda acdfgBin : acdfgBin.isolated,
             prefix_provenance)
  printNodes(lattice, dot_stream, stats,
             lambda acdfgBin : ((not acdfgBin.popular) and
                                (not acdfgBin.anomalous) and
                                (not acdfgBin.isolated)),
             prefix_provenance)
  # Create edges
  rel = trans_rel
  for (a,b) in rel:
    dot_stream.write("%d -> %d [label=\"%d -> %d\"]\n" % (a,b,a,b))
  dot_stream.write("}\n")


def get_repr_page(acdfgBin, prefix_provenance="./"):
  acdfg_proto = acdfgBin.acdfg_repr

  fname = ".".join(["_".join([acdfg_proto.source_info.class_name,
                              acdfg_proto.source_info.method_name]),
                    "html"])
  path = os.path.join(prefix_provenance,
                      acdfg_proto.repo_tag.user_name,
                      acdfg_proto.repo_tag.repo_name,
                      acdfg_proto.repo_tag.commit_hash,
                      fname)

  return path

def create_dot_acdfg_bin(acdfgBin, dot_stream, prefix_provenance=""):
  acdfg_proto = acdfgBin.acdfg_repr
  acdfg_repr = AcdfgRepr(acdfg_proto)
  acdfg_repr.print_dot(dot_stream, filter_set = {})

def create_svgs(svgs_file_path):
  for dotfile in os.listdir(svgs_file_path):
    if not dotfile.endswith(".dot"):
      continue

    basename = os.path.basename(dotfile)
    svgfile = "%s.svg" % basename[:-4]
    args = ["dot", "-Tsvg", "-o%s" % svgfile, basename]

    success = _call_sub(args, svgs_file_path)

    if not success:
      logging.warning("Error computing the svg images "
                      "for %s" % basename)


def print_lattices(lattice_file_path, out_dir, prefix_provenance):
  # Read lattice
  lattice = Lattice()
  with open(lattice_file_path,'rb') as file_lattice:
    lattice.ParseFromString(file_lattice.read())

    # Build the dot representation of the lattice
    outfile = os.path.join(out_dir, "out.dot")
    with open(outfile, "wt") as dot_stream:
      create_dot_lattice(lattice, dot_stream, prefix_provenance)

    # Create dot for bins
    for acdfgBin in lattice.bins:
      with open(os.path.join(out_dir, "%s.dot" % str(acdfgBin.id)), "wt") as dot_stream:
        create_dot_acdfg_bin(acdfgBin, dot_stream)


def print_clusters(cluster_path,
                   cluster_count, # all_clusters path
                   html_files_path,
                   gen_svgs=True,
                   prefix_provenance=None):

  logger = logging.getLogger(__name__)

  all_lattices_svgs=[]

  # Goes through the lattice files
  for cluster_index in range(int(cluster_count)):
    cluster_index = cluster_index + 1
    cluster_index_path = os.path.join(cluster_path, "all_clusters", "cluster_%d" % cluster_index)

    if (not os.path.isdir(cluster_index_path)):
      logger.debug("%s path does not exists" % cluster_index_path)

    lattice_path = os.path.join(cluster_index_path,
                                "cluster_%d_lattice.bin" % cluster_index)
    if (not os.path.isfile(lattice_path)):
      # This is ok, the lattice may have not been computed due to to
      logger.debug("Lattice %s does not exists" % lattice_path)

    out_dir = os.path.join(html_files_path, "cluster_%d" % cluster_index)
    all_lattices_svgs.append(os.path.join(out_dir, "out.svg"))

    try:
      os.mkdir(out_dir)

      print_lattices(lattice_path,
                     out_dir,
                     prefix_provenance)
      create_svgs(out_dir)
    except OSError as error:
      logger.debug("Error creating the output directory: %s" % out_dir)
    except Exception:
      logger.debug("Error creating the lattices for cluster:"
                   "%d" % cluster_index)

def main():
  logging.basicConfig(level=logging.DEBUG)
  logger = logging.getLogger(__name__)

  p = optparse.OptionParser()
  p.add_option('-l', '--lattice_file', help="Path to the lattice file to display")
  p.add_option('-o', '--output_folder', help="Path for the svg to output")
  p.add_option('-p', '--provenance_path', help="Path to the provenance folder (for cross links)")
  opts, args = p.parse_args()

  if not opts.lattice_file or not os.path.isfile(opts.lattice_file):
    print("Lattice not provided or not found")
    sys.exit(1)
  elif not opts.output_folder or not os.path.isdir(opts.output_folder):
    print("Output folder not provided")
    sys.exit(1)

  # prefix_provenance = "/Users/sergiomover/works/projects/muse/musedev_demo/other/datasets/provenance"
  if opts.provenance_path:
    prefix_provenance = opts.provenance_path
  else:
    prefix_provenance = ""

  lattice_file_path = opts.lattice_file
  out_dir = opts.output_folder

  print_lattices(lattice_file_path, out_dir, prefix_provenance)
  create_svgs(out_dir)


if __name__ == '__main__':
  main()



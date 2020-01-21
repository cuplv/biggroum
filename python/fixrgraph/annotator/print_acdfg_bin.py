#!/bin/python

""" Print a visualization of the lattice in html.

Start with building the DOT for the lattice.
"""

import logging
import os

import html

from string import Template
from fixrgraph.annotator.protobuf.proto_acdfg_pb2 import Acdfg
from fixrgraph.annotator.protobuf.proto_acdfg_bin_pb2 import Lattice
from collections import deque

# Weird circular dependency
from fixrsearch.codegen.acdfg_repr import AcdfgRepr

DOT_ACDFGBIN_DOT="""${ID} [shape=box,style=filled,color="${COLOR}",label="${LABEL} ${FREQUENCY} ${POPULARITY}",href="${HREF}"];
"""

DOT_ACDFGBIN_DOT="""${ID} [shape=box,style=filled,color="${COLOR}",
label=<<table>
<tr><td href="${PROVENANCE_PATH}">${LABEL} ${FREQUENCY} ${POPULARITY}</td></tr>
<tr><td href="${HREF}">pattern</td></tr>
</table>>];
"""

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

    (freq, pop) = stats[acdfgBin.id]

    node_repr = node_template.substitute(
      {"ID" : str(acdfgBin.id),
       "COLOR" : get_node_color(acdfgBin),
       "LABEL" : get_node_label(acdfgBin),
       "FREQUENCY" : freq,
       "POPULARITY" : pop,
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

      pop = get_freq(acdfgBin)
      while len(successors) > 0:
        nextId = successors.pop()
        nextBin = idToBin[nextId]
        pop += get_freq(nextBin)

        for (a, b) in trans_rel:
          if a == nextBin.id:
            successors.append(b)

      idToStats[acdfgBin.id] = (get_freq(acdfgBin), pop)
      visited.add(acdfgBin.id)
    else:
      to_visit.appendleft(acdfgBin)

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

def main():
  logging.basicConfig(level=logging.DEBUG)
  logger = logging.getLogger(__name__)

  prefix_provenance = "/Users/sergiomover/works/projects/muse/musedev_demo/other/datasets/provenance"

  lattice_file_path = "/Users/sergiomover/works/projects/muse/musedev_demo/other/clusters/all_clusters/cluster_31/cluster_31_lattice.bin" # toast

  cluster_id = 31 # toast
  # cluster_id = 171 # dialog
  # cluster_id = 675 # fragment transaction, preferences
  # cluster_id = 567 # db query, db close
  # cluster_id = 963 # color, only constatns and data flow, unuseful
  # cluster_id = 1083 # media player
  # cluster_id = 778 # SQL other stuff
  lattice_file_path = "/Users/sergiomover/works/projects/muse/musedev_demo/other/clusters/all_clusters/cluster_%s/cluster_%d_lattice.bin" % (cluster_id, cluster_id)

  # Read lattice
  lattice = Lattice()
  with open(lattice_file_path,'rb') as file_lattice:
    lattice.ParseFromString(file_lattice.read())

    # Build the dot representation of the lattice
    with open("out.dot", "wt") as dot_stream:
      create_dot_lattice(lattice, dot_stream, prefix_provenance)

    # Create dot for bins
    for acdfgBin in lattice.bins:
      with open("%s.dot" % str(acdfgBin.id), "wt") as dot_stream:
        create_dot_acdfg_bin(acdfgBin, dot_stream)



if __name__ == '__main__':
  main()



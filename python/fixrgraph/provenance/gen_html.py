""" Generate a set of html pages of the isomorphisms and an index to navigate and
search them.
"""

import sys
import os
import optparse
import logging
import string
import collections
import shutil

from fixrgraph.db.isodb import IsoDb

import collections

IsoInfo = collections.namedtuple("IsoInfo",
                                 ["isoname", "page", "weight"],
                                 verbose=False,
                                 rename=False)

index_template = \
"""<!DOCTYPE html>
<html>
<title>${TITLE}</title>
<body>

<h1>Subpages</h1>

${SUBPAGES}

</body>
</html>
"""

subpage_element = \
"""<p><a href="${PATH}">${NAME}</a></p>"""

iso_page = \
"""<!DOCTYPE html>
<html>
<script src="https://github.com/mdaines/viz.js/releases/download/v1.3.0/viz.js"></script>

<script>
var isoReq = new XMLHttpRequest();
isoReq.open('GET', './${DOTFILE}', true);
isoReq.send();
isoReq.onload = function() {
var isoText = isoReq.responseText;
var isoContainer = document.getElementById('iso');
var iso = Viz(isoText, options={ format: 'svg', engine: 'dot' });
isoContainer.innerHTML = iso;
};
</script>

<title>${TITLE}</title>
<body>

<h1>Isomorphism ${ISONAME}</h1>
<h2>Graph 1: <a href="${G1PAGE}">${G1}</a></h2>
<h2>Graph 2: <a href="${G2PAGE}">${G2}</a></h2>
<h2>Weight: ${WEIGHT}</h2>
<h2>Iso Bin path: ${ISOPATH}</h2>

<h2 id="iso"></h2>

</body>
</html>
"""




def _substitute(template, substitution):
    return string.Template(template).safe_substitute(substitution)



class Index(object):
    """ Entry of the index.

    An entry has a key and a map of childrens.

    The map has a key and an entry.
    """

    def __init__(self, key):
        self.key = key
        self.children = {}

    def has_child(self, child_key):
        """ Return true if the index has child_key as immediate child.
        """
        return child_key in self.children

    def get_child(self, child_key):
        """ Return the child with child_key.
        Precondition: child_key should be a child.
        """
        return self.children[child_key]

    def add_child(self, key, child):
        """ Add a child to this entry.
        """

        assert not self.has_child(key) # unique entry
        self.children[key] = child

    def _print(self, indent=""):
        print "%sKey: %s " % (indent, self.key)
        for c in self.children.itervalues():
            c._print(indent + "  ")

class Leaf(Index):
    """ Represent a leaf in the index.
    A leaf has no children.
    """
    def has_child(self, child_key):
        return False

    def get_child(self, child_key):
        return None

    def add_child(self, key, child):
        assert False

class HtmlCreator(object):
    """ Creates the index and the html pages for the isomorphisms."""

    def __init__(self, out_dir, graph_dir, prov_dir, iso_dir):
        self.out_dir = out_dir
        self.graph_dir = graph_dir
        self.prov_dir = prov_dir
        self.iso_dir = iso_dir

        # the root of the index kis out_dir
        self.index = Index(self.out_dir)
        # Max number of entries to write the index content on disc
        self.limit = 4000
        self.cache = []

    def flush(self):
        """ Writes all the pages and the index."""
        self._write_html_pages()
        # print index
        self.write_index()

    def _write_html_pages(self):
        """ Write the pages in the cache on disk. """
        for (path, page) in self.cache:
            dirs = os.path.dirname(path)
            if (not os.path.isdir(dirs)): os.makedirs(dirs)
            with open(path, 'w') as outfile:
                outfile.write(page)
                outfile.close()

    def write_index(self):
        index_page = self._write_index(self.index, '', [])

    def _write_index_page(self, indexfile, key, new_pages):
        # write the html index

        elems = []
        for (p, key) in new_pages:
            elems.append(_substitute(subpage_element, {"PATH" : p, "NAME" : key}))

        template = _substitute(index_template,
                               {"SUBPAGES" : "\n".join(elems),
                                "TITLE" : key})

        with open(indexfile, 'w') as fout:
            fout.write(template)
            fout.flush()
            fout.close()


    def _write_index(self, current, cpath, prev_pages):
        """ Write the index on disk."""

        if (isinstance(current, Leaf)):
            # Base case: leafadd the page
            # This is the isomorphism page
            iso_info = current.key
            assert isinstance(iso_info, IsoInfo)
            # TODO: make path relative
            prev_pages.append((iso_info.page, iso_info.isoname))
        else:
            # recur on the children
            #
            # Rational: write the index in the folder only if there
            # the node is a branch.
            # I.e. skip to write the index on a path of the tree
            #

            next_path = os.path.join(cpath, current.key)
            if (not os.path.exists(next_path)):
                os.makedirs(next_path)

            intermediate_index = False
            new_pages = [] # page indexes created in the children
            new_pages_count = 0
            for key, child in current.children.iteritems():
                new_pages = self._write_index(child, next_path, new_pages)
                intermediate_index = (intermediate_index or
                                      (len(new_pages) != 1 and len(new_pages) != new_pages_count))
                new_pages_count = len(new_pages)


            if (intermediate_index or current == self.index):
                # write the index
                indexfile = os.path.join(next_path, "index.html")
                indexfilerel = os.path.join(current.key, "index.html")

                assert not os.path.exists(indexfile)

                self._write_index_page(indexfile, current.key, new_pages)

                prev_pages.append((indexfilerel, current.key))
            else:
                for (p, key) in new_pages:
                    prev_pages.append((os.path.join(current.key, p),
                                       current.key + "/"  + key))

        return prev_pages


    def _insert(self, keys, key_index, data, current_index):
        """ Insert the data in the index using the
        given list of keys.

        keys: it is a list of strings
        key_index: the index in keys that we must process.
        data: the data to write in the index
        current_index:
        """

        len_keys = len(keys)
        assert (len_keys > 0)

        # Find the right position in the index
        for k in keys:
            if key_index == (len_keys - 1):
                # the last element is the page name.
                current_index.add_child(keys[key_index], Leaf(data))
            else:
                if current_index.has_child(k):
                    # get the entry in the index
                    current_index = current_index.get_child(k)
                else:
                    # create the entry in the index
                    child = Index(k)
                    current_index.add_child(k, child)
                    current_index = child
            key_index = key_index + 1

    def _annotate_jimple(self, isopath, g1path, g2path,
                         sliced_jimple_1,
                         sliced_jimple_2):
        # TODO implement
        # Output: html code that shows the jimple association
        return ""


    def create_page(self, iso):
        """ Create the index entries and the page for the isomorphism.
        isoname: name of the isomorphisms
        isopath: path of the isomorphism on disk
        g1name: name of the first graph
        g2name: name of the second graph
        weight: weight of the isomorphism
        """
        (isoname, isopath, g1name, g2name, g1path, g2path, weight) = iso

        # html page for the isomorphism
        html_name = isoname + ".html"
        isohtmlpath = "/".join(g1name.split("."))
        isohtmlpath = os.path.join(isohtmlpath, html_name)

        # Insert the page in the index
        keys = g1name.split(".")
        html_full_name = os.path.join("/".join(keys), html_name)

        # DEBUG
        # html_full_name = os.path.join(self.out_dir, html_full_name)
        html_full_name = os.path.join(self.iso_dir, html_full_name)
        keys.append(html_name)

        iso_data = IsoInfo(isoname, html_full_name, weight)
        self._insert(keys, 0, iso_data, self.index)

        src_isodot = os.path.join(self.iso_dir,
                                  isopath.replace(".iso.bin", ".dot"))
        isodot = os.path.basename(src_isodot)
        isodot_abs = os.path.join(os.path.dirname(html_full_name), isodot)

        if g1path.startswith("/"): g1path = "." + g1path
        if g2path.startswith("/"): g2path = "." + g2path

        sliced_jimple_1 = os.path.join(self.prov_dir,
                                       g1path.replace(".iso.bin", ".sliced.jimple"))
        sliced_jimple_2 = os.path.join(self.prov_dir,
                                       g2path.replace(".iso.bin", ".sliced.jimple"))

        g1page = os.path.join(self.prov_dir,
                              g1path.replace(".acdfg.bin", ".html"))
        g2page = os.path.join(self.prov_dir,
                              g2path.replace(".acdfg.bin", ".html"))

        annotatedjimple = self._annotate_jimple(isopath, g1path, g2path,
                                                sliced_jimple_1, sliced_jimple_2)
        html_page = _substitute(iso_page,
                                {"TITLE" : "",
                                 "ISONAME" : isoname,
                                 "G1" : g1name,
                                 "G2" : g2name,
                                 "G1PAGE" : g1page,
                                 "G2PAGE" : g2page,
                                 "WEIGHT" : str(weight),
                                 "ISOPATH" : isopath,
                                 "DOTFILE" : isodot,
                                 "ANNOTATEDJIMPLE" : annotatedjimple})

        self.cache.append((html_full_name, html_page))
        if (len(self.cache) > self.limit):
            self._write_html_pages()
            self.cache = []




def main():
    logging.basicConfig(level=logging.DEBUG)

    p = optparse.OptionParser()
    p.add_option('-d', '--db', help="Database with data")
    p.add_option('-o', '--out_dir', help="Output directory with the index")
    p.add_option('-g', '--graph_dir', help="Graph dir")
    p.add_option('-p', '--prov_dir', help="Provenance dir")
    p.add_option('-i', '--iso_dir', help="Isodir")
    opts, args = p.parse_args()
    def usage(msg=""):
        if msg: print "----%s----\n" % msg
        p.print_help()
        sys.exit(1)
    exists = [opts.graph_dir, opts.prov_dir, opts.iso_dir]
    for d in exists:
        if (not d): usage("Missing")
        elif (not os.path.isdir(d)): usage("%d does not exists" % d)
    if not opts.db: usage("Db path not provided")
    if not os.path.isfile(opts.db): usage("Db %s does not exists!" % opts.db)

    # Load the isos from the DB
    db = IsoDb(opts.db)
    qres = db.get_isos()

    i = 0
    html = HtmlCreator(opts.out_dir, opts.graph_dir,
                       opts.prov_dir, opts.iso_dir)
    for iso in qres:
        i = i + 1
        html.create_page(iso)
    html.flush()


if __name__ == '__main__':
    main()



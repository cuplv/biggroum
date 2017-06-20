# Utility scripts that adds the commit date to a list of ACDFGs.
#
#

import sys
import getpass
import sys
import os
import optparse
import time
import dateutil.parser
import functools
from fixrgraph.solr import pysolr 
from fixrgraph.solr.common import upload_pool



try:
    from github import Github
    from github.GithubException import RateLimitExceededException
except:
    print "Install the Github python library (e.g. pip install PyGitHub)"
    raise


class GithubQuery(object):
    def __init__(self, username, password):
        self.repo = {}
        self.commit = {}
        self.date = {}

        self.g = Github(username, password)

    def do_query(self, query):
        inserted = False        
        try:
            print "Querying..."
            res = query()
            inserted = True
        except RateLimitExceededException:
            print "Waiting for github API to be available..."
            time.sleep(5)
        return res


    def _get_repo(self, repo_name):
        # print "Get repo: %s" % (repo_name)
        if repo_name in self.repo:
            return self.repo[repo_name]
        else:                
            gc_fun = functools.partial(self.g.get_repo, full_name_or_id=repo_name, lazy = True)
            res = self.do_query(gc_fun)

            self.repo[repo_name] = res

            return res


    def _get_commit(self, repo_name, hash):
        # print "Get commit: %s %s" % (repo_name, hash)
        if hash in self.commit:
            return self.commit[hash]
        else:
            repo = self._get_repo(repo_name)
                
            gc_fun = functools.partial(repo.get_commit, sha = hash)
            res = self.do_query(gc_fun)

            self.commit[hash] = res

            return res


    def get_date(self, repo_name, hash):
        # print "Get date: %s %s" % (repo_name, hash)
        key = (repo_name, hash)
        if key in self.date:
            return self.date[key]
        else:
            commit = self._get_commit(repo_name, hash)
            commit_date = commit.raw_data["commit"]["committer"]["date"]

            self.date[key] = commit_date
            return commit_date        

    # dateutil.parser.parse(commit.raw_data["commit"]["committer"]["date"])



def write_date(query, solr, groum_date_hash, doc, doc_pool):
    # print "write date..."
    id = doc["id"]
    repo_name = doc["repo_sni"]
    hash = doc["hash_sni"]
    try:
        date = query.get_date(repo_name, hash)

        # print "set date in doc"
        doc["commit_date_sni"] = date
        del doc["_version_"]

        doc_pool.append(doc)
        # print "set date in doc"
        doc_pool = upload_pool(solr, 10000, doc_pool)    
        groum_date_hash[id] = date
        return (date, doc_pool)
    except:
        return (None, doc_pool)

def main():
    # Create the object used to query github
    sys.stdout.write("Insert github username: ")
    username = sys.stdin.readline().strip()
    p = getpass.getpass("Insert github password: ")
    query = GithubQuery(username, p)

    groum_date_hash = {}

    # Query solr
    solr = pysolr.Solr("http://localhost:8983/solr/groums")
    results = solr.search("*:*", rows=300000)

    c = 0
    tot = len(results)
    doc_pool = []
    threshold = 10000
    patterns = []
    for doc in results:
        c += 1
        if c % 10000 == 0:
            print("Processing %d/%d" % (c, tot))

        if "doc_type_sni" not in doc:
            print "Skipping..."
            continue

        doc_type = doc["doc_type_sni"]
        if str(doc_type) == "groum":
            id = doc["id"]
            if id in groum_date_hash:
                continue
            if "commit_date_sni" in doc:
                groum_date_hash[id] = doc["commit_date_sni"]
                continue
            else:
                (date, doc_pool) = write_date(query, solr, groum_date_hash, doc, doc_pool)
                print str(doc)
                print date
                sys.exit(0)


            # print "written date..."
        elif str(doc_type) == "pattern":
            patterns.append(doc)

    c = 0
    for doc_p in patterns:
        c += 1
        print("Processing %d/%d" % (c, len(patterns)))

        lower = None
        upper = None
        for groum_id in doc_p["groum_keys_t"]:
            if groum_id not in groum_date_hash:
                print "%s not processed" % groum_id
                continue

            groum_date = groum_date_hash[groum_id]
            groum_date_p = dateutil.parser.parse(groum_date)
            if lower is None or upper is None:                
                lower = (groum_date, groum_date_p)
                upper = lower

            else:
                if groum_date_p > upper[1]:
                    upper = (groum_date, groum_date_p)
                elif groum_date_p < lower[1]:
                    lower = (groum_date, groum_date_p)

        if lower is not None:
            assert upper is not None
            del doc_p["_version_"]
            doc_p["lower_date_sni"] = lower[0]
            doc_p["upper_date_sni"] = upper[0]
            doc_pool.append(doc_p)
            doc_pool = upload_pool(solr, threshold, doc_pool)

    doc_pool = upload_pool(solr, -1, doc_pool)


    sys.exit(0)



    # hlist = ["bda3480881a146cbce77fd475fa4881e2dbc660e",
    #          "679a59633fdd9f80e2e54a4c5fe2241f83181a40",
    #          "72d26a7ef7d2199f9235e758497ed92f8a850d16",
    #          "b867e4ba14a6881606f70ede06e7ef92111db397",
    #          "c65a66bbd0113ea6ddc7dc5c2ef1544b7d60d6de",
    #          "26d8a86b043934d7c0944419e82a25482edb5ced",
    #          "fefa155667ae56478bc259314eb0257bfab6c51a",
    #          "a7980072694e72e82762e63af66f5eca3e945695",
    #          "05359022593574cbaec066bfe4329f85063dea42",
    #          "f393001c9a7bea4b955d589f239b45aef18d11b1",
    #          "ea93af11888bfd8c3ff371058423edf3dda64ffc",
    #          "9a5e89f6cc9334b9fedf2bcae87c2e3ec8402326",
    #          "4cd13a6e98958d31619567649d8236e9657b718b",
    #          "d2fd8728723e2fe1f57265e8e6567b4346590fd5",
    #          "df11cee4141df2ad6ba67b900937168daaefaa9b",
    #          "6c963a0cc24667b55d6b85b69a34882166c75772",
    #          "b5eb97f66d80ac6ae70363beed2df0ae4381e931",
    #          "f74e042b524be8d8c74b12020d01f5a7dc121db7",
    #          "afdb512f2eb084919f038584e7d07aeff230430a",
    #          "68ccccc907e0357ddd55b371ac398cc4bdbc1c0f",
    #          "4f8708190ba944672278486912a679a1f154475d",
    #          "742d50dff1e51b5d3d0fa2a16b3639b681efe11b",
    #          "5f95388a625c0eb4251e48f41019c2c784284c66",
    #          "31c5faf6307ac30f4d2883a9a962aa1db30e7bd9",
    #          "2111ebfdfdfcaa71c3fcca2948aa3c00bf681123",
    #          "5b0ce56334ed953f46e87a452e4724b854b34f6b",
    #          "da3e8173cebc193358bb81a145c68af9d0926aad",
    #          "252defe44d75db525a5cba1ded3f96610ea37b6f",
    #          "f172feacf05c35d3877776449b3c7b216c932b8f",
    #          "7ce09a77630b5211b607e2cee0f2e76a57d3eb62",
    #          "516360e96e1ece2ec1d7062785dd7cfa9f468f62"]

    # for i in range(10):
    #     print "Processing %d..." % (i)
    #     for h in hlist:        
    #         date = query.get_date("cuplv/FixrGraph", h)
        


if __name__ == '__main__':
    main()


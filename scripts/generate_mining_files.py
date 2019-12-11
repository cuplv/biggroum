import os, sys
import optparse
import json

def generate(path):
    if (not os.path.isdir(path)):
        print("Error: directory \"%s\" does not exist" % path)
    if (not os.path.exists("mining_configuration")):
        os.mkdir("mining_configuration")
        
    repo_list = []

    for root, dirs, files in os.walk(path):
        if "completed.txt" in files:
            data = {}
            meta_path = os.path.join(root, "meta.txt")
            with open(meta_path) as json_file:
                metadata = json.load(json_file)
                data["hash"] = metadata["versionName"]
                data["user_name"] = "fdroid"
                data["repo_name"] = metadata["packageName"]
            repo_list.append(data)
    with open("mining_configuration/repo_list.json", "w") as f:
        json.dump(repo_list, f, indent=4, sort_keys=True)

    
    
                

def main():
    p = optparse.OptionParser()
    p.add_option('-p', '--path', help="Path to directory containing data")
    opts, args = p.parse_args()

    def usage(msg=""):
        if msg:
            print "----%s----\n" % msg
        p.print_help()
        sys.exit(1)

    if (not opts.path):
        usage("No path specified")

    generate(opts.path)

if __name__ == "__main__":
    main()

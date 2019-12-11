import os, sys
import optparse
import json
import shutil
import tarfile


class IDGen:
    current_id = 1
    @staticmethod
    def getId():
        tmp = IDGen.current_id
        IDGen.current_id += 1
        return tmp

def find_with_extension(path, extension):
    paths = []
    for root,dirs,files in os.walk(path):
        for f in files:
            if f.endswith(extension):
                paths.append(os.path.join(root,f))
    return paths

def generate_repo_list(path,out_path = None, extract_sources=None):
    if out_path is None:
        out_path = "./"
    elif not os.path.isdir(out_path):
        raise Exception("Output directory %s does not exist" % out_path)
    if (not os.path.isdir(path)):
        print("Error: directory \"%s\" does not exist" % path)
    if (not os.path.exists(os.path.join(out_path,"mining_configuration"))):
        os.mkdir("mining_configuration")
        
    repo_list = []
    buildable_list = []

    for root, dirs, files in os.walk(path):
        if "completed.txt" in files:
            print("Processing directory %s" % root)
            data = generate_repo_list_item(root)
            repo_list.append(data)
            buildable_list.append(generate_build_list_item(root, extract_sources))
    with open(os.path.join(out_path,"mining_configuration/repo_list.json"), "w") as f:
        json.dump(repo_list, f, indent=4, sort_keys=True)
    with open(os.path.join(out_path,"mining_configuration","buildable.json"),'w') as f:
        json.dump({"results": buildable_list}, f, indent=4, sort_keys=True)
    return repo_list


def generate_repo_list_item(fdroid_project_base_dir):
    data = {}
    meta_path = os.path.join(fdroid_project_base_dir, "meta.txt")
    with open(meta_path) as json_file:
        metadata = json.load(json_file)
        data["hash"] = metadata["versionName"]
        # user name is containing directory for compatibility
        data["user_name"] = fdroid_project_base_dir.split(os.sep)[-1]
        data["repo_name"] = metadata["packageName"]
    return data

def extract_all(base_dir):
    for root,dirs,files in os.walk(base_dir):
        for fname in files:
            fpath = os.path.join(root,fname)
            if (fname.endswith("tar.gz")):
                tar = tarfile.open(fpath, "r:gz")
                tar.extractall(base_dir)
                tar.close()
            elif (fname.endswith("tar")):
                tar = tarfile.open(fpath, "r:")
                tar.extractall(base_dir)
                tar.close()

def generate_build_list_item(fdroid_project_base_dir, extract_sources=None):
    data = {}
    data["_id"] = IDGen.getId()
    spl = fdroid_project_base_dir.split(os.sep)
    data["hash"] = spl[-1]
    data["repo"] = spl[-2]
    data["user"] = spl[-3]
    bin_data = {}
    apk_paths = [p.split(fdroid_project_base_dir)[1] for p in find_with_extension(fdroid_project_base_dir,".apk")]
    bin_data["apk"] = apk_paths
    bin_data["jar"] = []
    bin_data["src"] = []
    bin_data["cls"] = []

    if extract_sources is not None:
        outerdir = os.path.join(extract_sources,spl[-3])
        if (not os.path.isdir(outerdir)):
            os.mkdir(outerdir)
        tmpsrc = os.path.join(extract_sources, spl[-3], spl[-2])
        # os.mkdir(tmpsrc)
        shutil.copytree(fdroid_project_base_dir, tmpsrc)
        extract_all(tmpsrc)
        bin_data["src"] = find_with_extension(tmpsrc, ".java")
    data["apps"] = {"bin": bin_data}

    return data




def main():
    p = optparse.OptionParser()
    p.add_option('-p', '--path', help="Path to directory containing data")
    p.add_option('-o', '--output_path', help="directory to output config files")
    p.add_option('-e', '--extract_src_dir',
                 help="Optional: directory to extract sources zip, do not put inside fdroid folder")
    opts, args = p.parse_args()

    def usage(msg=""):
        if msg:
            print "----%s----\n" % msg
        p.print_help()
        sys.exit(1)

    if (not opts.path):
        usage("No path specified")

    generate_repo_list(opts.path, opts.output_path, opts.extract_src_dir)

if __name__ == "__main__":
    main()

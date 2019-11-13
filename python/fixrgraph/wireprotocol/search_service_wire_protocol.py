from zipfile import ZipFile
import os
import requests

def compress(in_dir, name):
    """
    :param zipdir: a directory to compress
    :param name: name of (or path to) the new zip, e.g., "new.zip"
    :return: path to compressed zip
    """
    with ZipFile(name, 'w') as z:
        for root, dirs, files in os.walk(in_dir):
            for file in files:
                infilepath = os.path.join(root, file)
                arcname = os.sep.join([in_dir.split(os.sep)[-1],infilepath.split(in_dir)[1]])
                z.write(infilepath,arcname)
        path = z.filename
    return path

def decompress(zip_file, unzip_path):
    """
    :param zip_file: path to zip
    :param unzip_path: directory to extract to
    :return: None
    """
    with ZipFile(zip_file) as z:
        z.extractall(unzip_path)

def send_zips(graphs_path, sources_path):
    endpoint = os.getenv("FIXR_ENDPOINT")
    with open(graphs_path,'rb') as graphs_file:
        with open(sources_path,'rb') as sources_file:
            r = requests.post(endpoint, files={'src':sources_file,'graph':graphs_file})
    return r

from zipfile import ZipFile

def compress(file_list, name):
    """
    :param file_list: a list of strings representing fully qualified paths to files
    :param name: name of (or path to) the new zip, e.g., "new.zip"
    :return: path to compressed zip
    """
    with ZipFile(name, 'w') as z:
        for f in file_list:
            z.write(f)
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

import os
import logging
import re
from xml.dom.minidom import parse, parseString


def write_log(log, repo, msg, level="error"):
    log_msg = "%s: %s" % (str(repo), msg)
    if (log != None):
        if level == "error":
            log.error(log_msg)
        if level == "debug":
            log.debug(log_msg)
        if level == "info":
            log.info(log_msg)
    else:
        logging.debug(log_msg)

def get_android_jar(android_home, version):
    """Find the right android.jar"""
    jar_path = os.path.join(android_home, "platforms", "android-%s" % version, "android.jar")
    
    if not os.path.isfile(jar_path):
        msg = "Cannot find the jar %s" % (jar_path)
        logging.debug(msg)
        return None
    else:
        return jar_path

def search_classes(repo_dir, gradle_file_path):
    """Looks for the classes.jar file created during the build"""
    logging.info("Searching main classes %s " % str(gradle_file_path))

    manifest = None
    for root, dirs, files in os.walk(gradle_file_path):
        if "AndroidManifest.xml" in files:
            manifest = os.path.join(root, "AndroidManifest.xml")
            break

    if None != manifest:
        # get the package name manifest, package
        #
        # get the application, android:name tag
        #
        dom1 = parse(manifest)
        manifest_node = dom1.getElementsByTagName('manifest')
        if (len(manifest_node) > 0):
            if None != manifest_node[0].attributes and 'package' in manifest_node[0].attributes.keys():
                packageName = str(manifest_node[0].attributes['package'].value)
                # OS dependent
                packagePath = packageName.replace(".", "/")

                # search for package name and classes
                classes = []
                for root, dirs, files in os.walk(repo_dir):
                    if packagePath in str(root):
                        for f in files:
                            str_f = str(f)
                            if str_f.endswith(".class"):
                                classes.append(os.path.join(root, f))

                if len(classes) > 0:
                    for c in classes:
                        try:
                            c_str = str(c)
                            index = c_str.index(packagePath)
                            base_path = c_str[:index]
                            # pick the first one.
                            logging.debug("Base path for %s is %s" % (repo_dir,base_path))
                            return base_path
                        except ValueError:
                            # do nothing.
                            base_path = None
        logging.debug("Cannot find base path for %s" % (repo_dir))
        return None

def get_repo_url(user_name, repo_name):
    repo_url = "https://github.com/%s/%s" % (user_name, repo_name)
    return repo_url

def get_repo_path(dir_path, repo):
    """Return the path of the repository relative to dir_path.
    dir_path is either the input or the output directory.
    """
    if(len(repo) > 2):
        repo_path = os.path.join(dir_path, repo[0], repo[1], repo[2])
    else:
        repo_path = os.path.join(dir_path, repo[0], repo[1], "head")
    return repo_path

def get_repo_name(repo):
    return "%s/%s" % (repo[0], repo[1])

"""Get the min/max SDK version used by the app."""
def matchNumber(key, startstring):
    key = key.strip()
    startstring = startstring.strip()
    if not startstring.startswith(key):
        return None
    match = re.search('^%s ([0-9]+)' % key, (startstring))
    if match:
        number = match.group(1)
        return int(number)
    return None

def get_version_from_gradle(gradle_build_file):
    """ Returns the value of the attributes:
    (minSdkVersion, maxSdkVersion, compileSdkVersion
    """
    def getLimit(current, new, is_min):
        if (is_min and new != None and
                (new < current or current == None)):
            return new
        if (is_min and new != None and
                (new > current or current == None)):
            return new
        return current

    android_version = None
    min_sdk_version = None
    max_sdk_version = None

    with open(gradle_build_file, 'r') as f:
        for l in f.readlines():
            new_min = matchNumber("minSdkVersion", l)
            new_max = matchNumber("maxSdkVersion", l)

            match = re.search('^compileSdkVersion ([0-9]+)', l.strip())
            if match:
                version_number =  match.group(1)
            else:
                version_number = None

            min_sdk_version = getLimit(min_sdk_version, new_min, True)
            max_sdk_version = getLimit(max_sdk_version, new_max, False)
            if (version_number != None):
                android_version = version_number

    return (min_sdk_version, max_sdk_version, android_version)


def find_gradle_file(repo_folder):
    """Find the build.gradle file in the repository.
    Return either the path to a build.gradle file or None.
    """
    gradle_build_name = "build.gradle"

    for root, dirs, files in os.walk(repo_folder, topdown=True):
        if gradle_build_name in files:
            return os.path.join(root, gradle_build_name)

    return None

def getGradleInfo(repo, repo_folder):
    # Current heuristic to build an android app
    # 1. Find the build.gradle file (find the first in the repo tree)
    #
    # Decision making:
    #   - we need to find at least one build.gradle
    #

    gradle_build_file = find_gradle_file(repo_folder)
    if (None == gradle_build_file):
        return (None, None)

    gradle_path = os.path.dirname(gradle_build_file)

    return (gradle_build_file, gradle_path)

def getAndroidAppPlugin(log, repo, repo_folder):
    gradle_build_name = "build.gradle"

    (gradle_build_file, basePath) = getGradleInfo(repo, repo_folder)
    if (None == gradle_build_file):
        # Skip if there is no build.gradle
        write_log(log, repo, "Gradle file found.")
        return None

    assert (os.path.exists(basePath))

    gradles_for_app = []
    for root, dirs, files in os.walk(basePath, topdown=True):
        if gradle_build_name in files:
            gradle_file = os.path.join(root, gradle_build_name)
            with open(gradle_file, 'r') as gradleFile:
                for line in gradleFile:
                    if "com.android.application" in line:
                        gradles_for_app.append(gradle_file)
                        break

    if (len(gradles_for_app) < 1):
        msg = "No builds for app in %s/%s" % (repo[0], repo[1])
        logging.debug(msg)
        write_log(log, repo, msg)
    elif (len(gradles_for_app) > 1):
        gradles_for_app = [l for l in gradles_for_app if not "wear" in l]
        if (len(gradles_for_app) > 1):
            # Found more apps
            logging.debug("Found more builds for apps for %s/%s" % (repo[0], repo[1]))
            message = "Found more builds for apps for %s/%s" % (repo[0], repo[1])
            for g in gradles_for_app:
                message = message + "\n" + g
            write_log(log, repo, message)
            return None

    if (len(gradles_for_app) > 0):
        gradle_path = os.path.dirname(gradles_for_app[0])
    else:
        return None
    return gradle_path

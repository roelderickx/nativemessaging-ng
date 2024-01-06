# -*- coding: utf-8 -*-

import sys
import os
import argparse
import logging
import json
if sys.platform == "win32":
    import winreg

from .version import __program__, __version__

# locations for storing manifests
browser_info = {
    "chrome": {
        "registry": "Software\\Google\\Chrome\\NativeMessagingHosts",
        "linux": os.path.join(os.path.expandvars("$HOME"), ".config/google-chrome/NativeMessagingHosts"),
        "darwin": os.path.join(os.path.expandvars("$HOME"), "Library/Application Support/Google/Chrome/NativeMessagingHosts")
    },
    "firefox": {
        "registry": "Software\\Mozilla\\NativeMessagingHosts",
        "linux": os.path.join(os.path.expandvars("$HOME"), ".mozilla/native-messaging-hosts"),
        "darwin": os.path.join(os.path.expandvars("$HOME"), "Library/Application Support/Mozilla/NativeMessagingHosts")
    }
}

def read_file(filename):
    with open(filename, "r") as f:
        return f.read()


def write_file(filename, contents):
    with open(filename, "w") as f:
        f.write(contents)


def write_manifest(browser, path, manifest, logger):
    if browser == "firefox":
        manifest.pop("allowed_origins", None)
    elif browser == "chrome":
        manifest.pop("allowed_extensions", None)

    write_file(path, json.dumps(manifest))
    logger.debug("Saved manifest file to %s" % path)


def create_reg_key(path, value, logger):
    winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)
    registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_WRITE)
    winreg.SetValue(registry_key, "", winreg.REG_SZ, value)
    winreg.CloseKey(registry_key)

    logger.info("Created registry key at HKEY_CURRENT_USER\\%s" % path)


def install_windows(browsers, manifest, logger):
    install_dir = os.path.dirname(manifest["path"])

    if manifest["path"].endswith(".py"):
        # create batch file for python apps in windows
        batch_path = os.path.join(install_dir, manifest["name"] + ".bat")
        write_file(batch_path, "@echo off\npython -u \"{0}\"".format(manifest["path"]))
        manifest["path"] = batch_path
        logger.debug("Batch file created at %s" % manifest["path"])

    # write registry key on windows
    for browser in browsers:
        manifest_path = os.path.join(install_dir, "{0}_{1}.json".format(manifest["name"], browser))
        write_manifest(browser, manifest_path, manifest, logger)
        create_reg_key(os.path.join(browser_info[browser]["registry"], manifest["name"]),
                       manifest_path, logger)


def install_unix(browsers, manifest, logger):
    for browser in browsers:
        manifest_path_folder = browser_info[browser][sys.platform]
        if not os.path.exists(manifest_path_folder):
            os.mkdir(manifest_path_folder)
        manifest_path = os.path.join(manifest_path_folder, manifest["name"] + ".json")
        write_manifest(browser, manifest_path, manifest, logger)


def install(browsers, manifest_filename):
    logger = logging.getLogger(__program__)

    # read contents of manifest file
    logger.info("Reading manifest %s" % manifest_filename)
    manifest_contents = None
    try:
        manifest_contents = read_file(manifest_filename)
    except:
        logger.error("Could not open file %s for reading." % manifest_filename)
        raise

    manifest = None
    try:
        manifest = json.loads(manifest_contents)
    except:
        logger.error("%s is not a valid json formatted file." % manifest_filename)
        raise

    # ensure path is absolute
    manifest["path"] = os.path.abspath(manifest["path"])
    logger.debug("Absolute path: %s" % manifest["path"])

    if sys.platform == "win32":
        install_windows(browsers, manifest, logger)
    elif sys.platform in ["linux", "darwin"]:
        install_unix(browsers, manifest, logger)


def parse_commandline(logger):
    parser = argparse.ArgumentParser(prog="nativemessaging-install")
    parser.add_argument("--version", action="version",
                        version="%s %s" % (__program__, __version__))
    parser.add_argument("--manifest", dest="manifest", type=str, metavar="MANIFEST",
                        default="native-manifest.json",
                        help="path to the manifest file to install (default: %(default)s)")
    parser.add_argument("browsers", metavar="BROWSER", choices=[ "chrome", "firefox" ], nargs="+",
                        help="browser(s) for which the manifest will be installed, " +
                             "valid values are chrome or firefox.")

    params = parser.parse_args()

    return params


def main():
    logger = logging.getLogger(__program__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

    params = parse_commandline(logger)

    if not os.path.isfile(params.manifest):
        logger.error("Manifest file %s not found." % params.manifest)
    else:
        install(params.browsers, params.manifest)

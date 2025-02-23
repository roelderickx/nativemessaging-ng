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
unix_home_dir = os.path.expandvars("$HOME")
browser_info = {
    "chrome": {
        "registry": "Software\\Google\\Chrome\\NativeMessagingHosts",
        "linux": os.path.join(unix_home_dir, ".config/google-chrome/NativeMessagingHosts"),
        "darwin": os.path.join(unix_home_dir, "Library/Application Support/Google/Chrome/NativeMessagingHosts")
    },
    "chromium": {
        "registry": "Software\\Google\\Chrome\\NativeMessagingHosts",
        "linux": os.path.join(unix_home_dir, ".config/chromium/NativeMessagingHosts"),
        "darwin": os.path.join(unix_home_dir, "Library/Application Support/Chromium/NativeMessagingHosts")
    },
    "firefox": {
        "registry": "Software\\Mozilla\\NativeMessagingHosts",
        "linux": os.path.join(unix_home_dir, ".mozilla/native-messaging-hosts"),
        "darwin": os.path.join(unix_home_dir, "Library/Application Support/Mozilla/NativeMessagingHosts")
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
        write_file(path, json.dumps(manifest))
    elif browser in ("chrome", "chromium"):
        manifest.pop("allowed_extensions", None)
        write_file(path, json.dumps(manifest, ensure_ascii=False))

    logger.debug("Saved manifest file to %s" % path)


def read_reg_key(path, logger):
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_READ)
        value, regtype = winreg.QueryValueEx(registry_key, "")
        winreg.CloseKey(registry_key)

        logger.info("Registry value at HKEY_CURRENT_USER\\%s is %s" % (path, value))
        
        return value
    except WindowsError:
        logger.error("Could not read registry key %s" % path)
        return None


def create_reg_key(path, value, logger):
    try:
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(registry_key, "", 0, winreg.REG_SZ, value)
        winreg.CloseKey(registry_key)

        logger.info("Created registry key at HKEY_CURRENT_USER\\%s" % path)
    except WindowsError:
        logger.error("Could not write registry key %s" % path)
        raise


def delete_reg_key(path, logger):
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_ALL_ACCESS)
        winreg.DeleteValue(registry_key, "")
        winreg.CloseKey(registry_key)

        logger.info("Deleted registry value at HKEY_CURRENT_USER\\%s" % path)
    except WindowsError:
        logger.error("Could not delete registry key %s" % path)
        raise


def install_windows(browsers, manifest, logger):
    manifest_path = os.path.dirname(manifest["path"])

    if manifest["path"].endswith(".py"):
        # create batch file for python apps in windows
        batch_file = os.path.join(manifest_path, manifest["name"] + ".bat")
        write_file(batch_file, '@echo off\r\npython -u "%s"' % manifest["path"])
        manifest["path"] = batch_file
        logger.debug("Batch file created at %s" % manifest["path"])

    # write registry key on windows
    for browser in browsers:
        manifest_file = os.path.join(manifest_path, "%s_%s.json" % (manifest["name"], browser))
        write_manifest(browser, manifest_file, manifest, logger)
        create_reg_key(os.path.join(browser_info[browser]["registry"], manifest["name"]),
                       manifest_file, logger)


def install_unix(browsers, manifest, logger):
    for browser in browsers:
        manifest_path = browser_info[browser][sys.platform]
        if not os.path.exists(manifest_path):
            os.mkdir(manifest_path)
        manifest_file = os.path.join(manifest_path, manifest["name"] + ".json")
        write_manifest(browser, manifest_file, manifest, logger)


def install(browsers, manifest_filename):
    '''
    Installes the manifest file in the configuration of the given browser(s).
    '''
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


def is_installed_windows(application_name, logger):
    browsers = []

    for browser in browser_info.keys():
        manifest_file = \
            read_reg_key(os.path.join(browser_info[browser]["registry"], application_name), logger)
        if manifest_file and os.path.exists(manifest_file):
            browsers.append(browser)

    return browsers


def is_installed_unix(application_name, logger):
    browsers = []

    for browser in browser_info.keys():
        manifest_path = browser_info[browser][sys.platform]
        if os.path.exists(manifest_path):
            manifest_file = os.path.join(manifest_path, application_name + ".json")
            if os.path.exists(manifest_file):
                browsers.append(browser)

    return browsers


def is_installed(application_name):
    '''
    Returns a list of browsers having the nativemessaging manifest for application_name installed.
    '''
    logger = logging.getLogger(__program__)

    if sys.platform == "win32":
        return is_installed_windows(application_name, logger)
    elif sys.platform in ["linux", "darwin"]:
        return is_installed_unix(application_name, logger)
    else:
        return [ ]


def uninstall_windows(browsers, application_name, logger):
    # delete registry key on windows
    for browser in browsers:
        manifest_file = \
            read_reg_key(os.path.join(browser_info[browser]["registry"], application_name), logger)
        '''
        TODO: check if we wrote the batch file, otherwise do not delete
        try:
            manifest_contents = read_file(manifest_filename)
            manifest = json.loads(manifest_contents)
            if manifest['path'].endswith(".bat"):
                os.remove(manifest['path'])
        except:
            pass
        '''
        os.remove(manifest_file)
        delete_reg_key(os.path.join(browser_info[browser]["registry"], application_name), logger)


def uninstall_unix(browsers, application_name, logger):
    for browser in browsers:
        manifest_path = browser_info[browser][sys.platform]
        manifest_file = os.path.join(manifest_path, application_name + ".json")
        os.remove(manifest_file)


def uninstall(browsers, application_name):
    '''
    Uninstalls the manifest file from browsers
    '''
    logger = logging.getLogger(__program__)

    if sys.platform == "win32":
        uninstall_windows(browsers, application_name, logger)
    elif sys.platform in ["linux", "darwin"]:
        uninstall_unix(browsers, application_name, logger)


def parse_commandline(logger):
    parser = argparse.ArgumentParser(prog="nativemessaging-ng")
    parser.add_argument("--version", action="version",
                        version="%s %s" % (__program__, __version__))
    parser.add_argument("action", choices=[ "install", "verify", "uninstall" ],
                        help="action to take, can be install, verify or uninstall")
    parser.add_argument("--manifest", dest="manifest", type=str, metavar="MANIFEST",
                        default="native-manifest.json",
                        help="path to the manifest file to install (default: %(default)s)")
    parser.add_argument("--appname", dest="appname", type=str, metavar="NAME",
                        help="application name to be verified or uninstalled")
    parser.add_argument("browsers", metavar="BROWSER",
                        choices=[ "chrome", "chromium", "firefox" ], nargs="+",
                        help="browser(s) for which the manifest will be installed, " +
                             "valid values are chrome, chromium or firefox.")

    params = parser.parse_args()
    
    if params.action in [ "verify", "uninstall" ] and not params.appname:
        parser.error("Application name is required when action is verify or uninstall")

    return params


def main():
    logger = logging.getLogger(__program__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    
    params = parse_commandline(logger)

    if params.action == "verify":
        installed_browsers = is_installed(params.appname)
        everywhere_installed = True
        for browser in params.browsers:
            if browser not in installed_browsers:
                everywhere_installed = False

        if everywhere_installed:
            logger.info("%s is installed in %s" % (params.appname, ", ".join(params.browsers)))
        else:
            logger.info("%s is not installed in %s" % \
                                    (params.appname, ", ".join(params.browsers)))
    elif params.action == "uninstall":
        uninstall(params.browsers, params.appname)
    elif not os.path.isfile(params.manifest):
        logger.error("Manifest file %s not found." % params.manifest)
    else:
        install(params.browsers, params.manifest)

  $ [ "$0" != "/bin/bash" ] || shopt -s expand_aliases
  $ [ -n "$PYTHON" ] || PYTHON="`which python`"
  $ alias nativemessaginginstall="PYTHONPATH=$TESTDIR/.. $PYTHON -m nativemessaging"

usage:
  $ nativemessaginginstall -h
  usage: nativemessaging-install [-h] [--version] [--manifest MANIFEST]
                                 [--appname NAME]
                                 {install,verify,uninstall} BROWSER
                                 [BROWSER ...]
  
  positional arguments:
    {install,verify,uninstall}
                          action to take, can be install, verify or uninstall
    BROWSER               browser(s) for which the manifest will be installed,
                          valid values are chrome, chromium or firefox.
  
  options:
    -h, --help            show this help message and exit
    --version             show program's version number and exit
    --manifest MANIFEST   path to the manifest file to install (default: native-
                          manifest.json)
    --appname NAME        application name to be verified or uninstalled

is_installed_before:
  $ nativemessaginginstall verify firefox --appname test
  test is not installed in firefox

install-wrong-manifest:
  $ nativemessaginginstall install firefox
  Manifest file native-manifest.json not found.

install:
  $ nativemessaginginstall install firefox --manifest $TESTDIR/test-manifest.json
  Reading manifest .*/test-manifest.json (re)
  Absolute path: .*/test.py (re)
  Saved manifest file to .*/test.json (re)

is_installed_after:
  $ nativemessaginginstall verify firefox --appname test
  test is installed in firefox

is_installed_chrome:
  $ nativemessaginginstall verify chrome --appname test
  test is not installed in chrome

uninstall:
  $ nativemessaginginstall uninstall firefox --appname test


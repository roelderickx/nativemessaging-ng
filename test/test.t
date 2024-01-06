  $ [ "$0" != "/bin/bash" ] || shopt -s expand_aliases
  $ [ -n "$PYTHON" ] || PYTHON="`which python`"
  $ alias nativemessaginginstall="PYTHONPATH=$TESTDIR/.. $PYTHON -m nativemessaging"

usage:
  $ nativemessaginginstall -h
  usage: nativemessaging-install [-h] [--version] [--manifest MANIFEST]
                                 [--verify NAME]
                                 BROWSER [BROWSER ...]
  
  positional arguments:
    BROWSER              browser(s) for which the manifest will be installed,
                         valid values are chrome or firefox.
  
  options:
    -h, --help           show this help message and exit
    --version            show program's version number and exit
    --manifest MANIFEST  path to the manifest file to install (default: native-
                         manifest.json)
    --verify NAME        tests if application name is installed in all given
                         browsers

is_installed_before:
  $ nativemessaginginstall --verify test firefox
  test is not installed in firefox

install-wrong-manifest:
  $ nativemessaginginstall firefox
  Manifest file native-manifest.json not found.

install:
  $ nativemessaginginstall --manifest $TESTDIR/test-manifest.json firefox
  Reading manifest .*/test-manifest.json (re)
  Absolute path: .*/test.py (re)
  Saved manifest file to .*/test.json (re)

is_installed_after:
  $ nativemessaginginstall --verify test firefox
  test is installed in firefox

is_installed_chrome:
  $ nativemessaginginstall --verify test chrome
  test is not installed in chrome


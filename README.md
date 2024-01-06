# nativemessaging-ng
A Python package for interfacing with Native Messaging in WebExtensions. Based on the apparently unmaintained version of [Rayquaza01](https://github.com/Rayquaza01/nativemessaging), which is in turn based on [Native Messaging on MDN](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_messaging#App_side) and [native-messaging on mdn/webextension-examples](https://github.com/mdn/webextensions-examples/tree/master/native-messaging).

## Native Messaging documentation
* [Native Messaging on MDN](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_messaging)
* [Native Messaging on Chrome Docs](https://developer.chrome.com/extensions/nativeMessaging)

## Installation

`pip3 install nativemessaging-ng`

## Usage

### Methods
The `nativemessaging` module exposes following methods:

* `log_browser_console(message)` will add the given message to the browser log (accessible via ctrl-shift-J)

* `get_message()` will poll for a message from the browser.
  If [runtime.connectNative](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/runtime/connectNative) is used, `get_message()` must be called repeatedly in a loop to poll for messages; if [runtime.sendNativeMessage](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/runtime/sendNativeMessage) is used, `get_message()` only needs to be called once.

* `send_message(message)` will send the given message to the browser.

* `install(browsers, manifest_filename)` takes a list of browsers to install the manifest and a manifest filename, to install the given manifest in the browser configuration. Supported browsers are 'chrome' and 'firefox'.

* `is_installed(application_name)` returns the list of browsers for which the manifest of application_name is installed.

#### Example
Browser side:
```javascript
function onReceived(response) {
    console.log(response);
}

// runtime.connectNative
var port = browser.runtime.connectNative("application_name");
port.onMessage.addListener(onReceived);
port.postMessage("hello");

// runtime.sendNativeMessage
browser.runtime.sendNativeMessage("application_name", "hello").then(onReceived);
```

Python application side:
```python
import nativemessaging

while True:
    message = nativemessaging.get_message()
    if message == "hello":
        nativemessaging.send_message("world")
```

### nativemessaging-install
`nativemessaging-install` is a command line script to install a manifest in the browser configuration.

```
usage: nativemessaging-install [-h] [--version] [--manifest MANIFEST]
                               BROWSER [BROWSER ...]

positional arguments:
  BROWSER              browser(s) for which the manifest will be installed,
                       valid values are chrome or firefox.

options:
  -h, --help           show this help message and exit
  --version            show program's version number and exit
  --manifest MANIFEST  path to the manifest file to install (default: native-
                       manifest.json)
```

#### Manifest file
The format of the manifest file must be similar to the native manifest format for Chrome or Firefox, with two main differences:
 * `path` must be a relative path to the native app in relation to your current working directory.
 * Both `allowed_extensions` and `allowed_origins` must be in the manifest to work with both Chrome and Firefox.
 
```json
{
    "name": "application_name",
    "description": "description",
    "path": "application_name.py",
    "type": "stdio",
    "allowed_extensions": ["extension@id"],
    "allowed_origins": ["chrome-extension://extension-id"]
}
```

#### Installed files
* Windows:
  - `<application_name>_firefox.json` and `<application_name>_chrome.json` will be created in `<path>`
  - A batch file will also be created to run the python application on Windows
  - A registry key is created at `HKEY_CURRENT_USER\Software\Google\Chrome\NativeMessagingHosts\<application_name>` or `HKEY_CURRENT_USER\Software\Mozilla\NativeMessagingHosts\<application_name>`

* Linux:
  - `~/.config/google-chrome/NativeMessagingHosts/<application_name>.json` or `~/.mozilla/native-messaging-hosts/<application_name>.json` will be created

* OS/X:
  - `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/<application_name>.json` or `~/Library/Application Support/Mozilla/NativeMessagingHosts/<application_name>.json` will be created


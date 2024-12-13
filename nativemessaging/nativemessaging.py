# -*- coding: utf-8 -*-

import json
import sys
import struct

def log_browser_console(message: str):
    '''
    Log a message in the browser console
    '''
    sys.stderr.write(message + '\n')


# from https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_messaging
def get_message_raw() -> str:
    '''
    Receive a native message from the browser
    '''
    raw_length = sys.stdin.buffer.read(4)
    if len(raw_length) == 0:
        return None
    message_length = struct.unpack("@I", raw_length)[0]
    message = sys.stdin.buffer.read(message_length).decode("utf-8")
    return message


def send_message_raw(message: str):
    '''
    Send a native message to the browser
    '''
    encoded_content = message.encode("utf-8")
    encoded_length = struct.pack("@I", len(encoded_content))
    sys.stdout.buffer.write(encoded_length)
    sys.stdout.buffer.write(encoded_content)
    sys.stdout.buffer.flush()


# from https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_messaging
def get_message() -> dict:
    '''
    Receive a native message from the browser and parse it as a json structure
    '''
    message = get_message_raw()
    if message:
        return json.loads(message)
    else:
        return None


def send_message(json_message: dict):
    '''
    Send a native message to the browser
    '''
    send_message_raw(json.dumps(json_message))

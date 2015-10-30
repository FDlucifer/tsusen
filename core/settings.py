#!/usr/bin/env python

"""
Copyright (c) 2015 Miroslav Stampar (@stamparm)
See the file 'LICENSE' for copying permission
"""

import os
import re
import socket
import stat
import subprocess

from core.attribdict import AttribDict

config = None

NAME = "tsusen"
VERSION = "0.1"
DEBUG = False
SNAP_LEN = 100
IPPROTO = 8
ETH_LENGTH = 14
IPPROTO_LUT = dict(((getattr(socket, _), _.replace("IPPROTO_", "")) for _ in dir(socket) if _.startswith("IPPROTO_")))
LOCAL_ADDRESSES = []
DATE_FORMAT = "%Y-%m-%d"
SYSTEM_LOG_DIRECTORY = "/var/log" if not subprocess.mswindows else "C:\\Windows\\Logs"
LOG_DIRECTORY = os.path.join(SYSTEM_LOG_DIRECTORY, NAME)
DEFAULT_LOG_PERMISSIONS = stat.S_IREAD | stat.S_IWRITE | stat.S_IRGRP | stat.S_IROTH
CSV_HEADER = "proto dst_port dst_ip src_ip first_seen last_seen count"
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HTML_DIR = os.path.join(ROOT_DIR, "html")
CONFIG_FILE = os.path.join(ROOT_DIR, "tsusen.conf")
DISABLED_CONTENT_EXTENSIONS = (".py", ".pyc", ".md", ".txt", ".bak", ".conf", ".zip", "~")
SERVER_HEADER = "%s/%s" % (NAME, VERSION)

def _read_config():
    global config

    if not os.path.isfile(CONFIG_FILE):
        exit("[!] missing configuration file '%s'" % CONFIG_FILE)
    elif not config:
        config = AttribDict()

        try:
            array = None
            content = open(CONFIG_FILE, "rb").read()

            for line in content.split("\n"):
                line = re.sub(r"#.+", "", line)
                if not line.strip():
                    continue

                if line.count(' ') == 0:
                    array = line.upper()
                    config[array] = []
                    continue

                if array and line.startswith(' '):
                    config[array].append(line.strip())
                    continue
                else:
                    array = None
                    name, value = line = line.strip().split(' ', 1)
                    name = name.upper()
                    value = value.strip("'\"")

                if name.startswith("USE_"):
                    value = value.lower() in ("1", "true")
                elif value.isdigit():
                    value = int(value)
                else:
                    for match in re.finditer(r"\$([A-Z0-9_]+)", value):
                        if match.group(1) in globals():
                            value = value.replace(match.group(0), globals()[match.group(1)])
                        else:
                            value = value.replace(match.group(0), os.environ.get(match.group(1), match.group(0)))
                    if subprocess.mswindows and "://" not in value:
                        value = value.replace("/", "\\")

                config[name] = value

        except (IOError, OSError):
            pass

        for option in ("MONITOR_INTERFACE",):
            if not option in config:
                exit("[!] missing mandatory option '%s' in configuration file '%s'" % (option, CONFIG_FILE))

if __name__ != "__main__" and config is None:
    _read_config()
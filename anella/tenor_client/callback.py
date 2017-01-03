#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Anella callbacks management"""

import requests
import json
import ConfigParser

CONFIG = ConfigParser.RawConfigParser()
CONFIG.read('config.cfg')

DEFAULT_CALLBACK_URL = CONFIG.get('service_manager', 'callback_url')

class Callback(object):
    """Represents a callback object"""

    def __init__(self, data, callback_url=DEFAULT_CALLBACK_URL):
        requests.post(callback_url,
                      headers={'Content-Type': 'application/json'},
                      json=data)

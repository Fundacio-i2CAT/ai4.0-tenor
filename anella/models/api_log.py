#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Api Log model"""

from mongoengine import *
import datetime

class ApiLog(Document):
    """APILog class"""

    method = StringField(required=True)
    data = StringField(required=True)
    timestamp = DateTimeField(default=datetime.datetime.now)

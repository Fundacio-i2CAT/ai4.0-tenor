#!/usr/bin/python
# -*- coding: utf-8 -*-
"""TeNOR messages models"""

from mongoengine import *
import datetime

class CriticalError(Document):
    """Critical Error"""

    service_instance_id = StringField(required=True)
    message = StringField(required=True)
    timestamp = DateTimeField(default=datetime.datetime.now)

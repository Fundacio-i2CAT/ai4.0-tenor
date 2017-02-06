#!/usr/bin/python
# -*- coding: utf-8 -*-
"""TeNOR messages models"""

from mongoengine import Document, StringField, DateTimeField
import datetime

class CriticalError(Document):
    """Critical Error"""

    service_instance_id = StringField(required=True)
    message = StringField(required=True)
    code = StringField(required=True)
    timestamp = DateTimeField(default=datetime.datetime.now)

class RegularMessage(Document):
    """Regular message"""

    service_instance_id = StringField(required=True)
    message = StringField(required=True)
    severity = StringField(required=True)
    module = StringField(required=True)
    timestamp = DateTimeField(default=datetime.datetime.now)

class MonitoringMessage(Document):
    """Monitoring message"""

    service_instance_id = StringField(required=True)
    message = StringField(required=True)
    timestamp = DateTimeField(default=datetime.datetime.now)

#!/usr/bin/python
# -*- coding: utf-8 -*-
"""TeNOR messages models"""

from mongoengine import Document, StringField, DateTimeField
import datetime

class MonitoringMockup(Document):
    """Monitoring message"""

    service_instance_id = StringField(required=True)
    message = StringField(required=True)
    timestamp = DateTimeField(default=datetime.datetime.now)


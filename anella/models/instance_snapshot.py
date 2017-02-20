#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Instance Configuration model"""

from mongoengine import StringField
from mongoengine import Document, DateTimeField
import datetime

class InstanceSnapshot(Document):
    """Instance snapshot class"""

    service_instance_id = StringField(required=True)
    image_id = StringField(required=True)
    name_image = StringField(required=True)
    timestamp = DateTimeField(default=datetime.datetime.now)


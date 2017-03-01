#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Instance Configuration model"""

from mongoengine import StringField
from mongoengine import Document, DateTimeField
import datetime

class InstanceMockup(Document):
    """Instance configuration class"""

    service_instance_id = StringField(required=True, unique=True)
    state = StringField(required=True)

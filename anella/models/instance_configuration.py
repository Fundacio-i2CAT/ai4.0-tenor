#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Instance Configuration model"""

from mongoengine import *

class InstanceConfiguration(Document):
    ns_instance_id = StringField(required=True)
    consumer_params = ListField(EmbeddedDocumentField(ConsumerParam))

if __name__ == "__main__":
    print "HOLA"


#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Consumer Param model"""

from mongoengine import *

class Field(EmbeddedDocument):
    name = StringField(required=True)
    value = StringField(required=True)
    desc = StringField(required=True)


class InstanceConfiguration(EmbeddedDocument):
    path = StringField(required=True)
    content = StringField(required=False)

if __name__ == "__main__":
    print "HOLA"

#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Consumer Param model"""

from mongoengine import EmbeddedDocument, StringField, ListField
from mongoengine import EmbeddedDocumentField, BooleanField

class ConsumerField(EmbeddedDocument):
    """Consumer field class"""

    name = StringField(required=True)
    value = StringField(required=True)
    desc = StringField(required=False)
    runtime = BooleanField(required=False)
    required = BooleanField(required=False)

class ConsumerParam(EmbeddedDocument):
    """Consumer param class"""

    path = StringField(required=True)
    content = StringField(required=False)
    fields = ListField(EmbeddedDocumentField(ConsumerField), required=False)

if __name__ == "__main__":
    FNAME = ConsumerField(name="name",
                          value="Alfonso Egio",
                          desc="Mi nombre")
    FPICTURE = ConsumerField(name="picture",
                          value="http://example.com/hola.jpg",
                          desc="URL de la foto")
    CP1 = ConsumerParam(path="/var/www/html", fields=[FNAME, FPICTURE])
    CP2 = ConsumerParam(path="/root/chequeo.txt", content="YO ESTUVE AQuÏ")

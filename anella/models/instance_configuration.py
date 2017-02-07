#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Instance Configuration model"""

from mongoengine import StringField, ListField
from mongoengine import EmbeddedDocumentField
from mongoengine import Document, DateTimeField
from mongoengine import connect
from consumer_param import ConsumerParam, ConsumerField
import datetime

class InstanceConfiguration(Document):
    """Instance configuration class"""

    service_instance_id = StringField(required=True)
    consumer_params = ListField(EmbeddedDocumentField(ConsumerParam))
    timestamp = DateTimeField(default=datetime.datetime.now)
    pkey = StringField(required=False)

def safe_encoding(thing):
    param_value = thing
    if type(param_value) == unicode:
        param_value = param_value.encode('utf-8')
    else:
        param_value = str(param_value)
    return param_value

def build_instance_configuration(service_instance_id, consumer_params, pkey):
    """Building it from array"""
    cpds = []
    for cpar in consumer_params:
        if 'content' in cpar:
            cpds.append(ConsumerParam(path=cpar['path'], content=cpar['content']))
            continue
        if 'fields' in cpar:
            fields = []
            for fpar in cpar['fields']:
                desc = None
                runtime = None
                required = None
                if 'desc' in fpar:
                    desc = fpar['desc']
                if 'runtime' in fpar:
                    runtime = fpar['runtime']
                if 'required' in fpar:
                    required = fpar['required']
                fields.append(ConsumerField(name=safe_encoding(fpar['name']),
                                            desc=safe_encoding(desc),
                                            value=safe_encoding(fpar['value']),
                                            required=required,
                                            runtime=runtime))
            cpds.append(ConsumerParam(path=cpar['path'], fields=fields))
    return InstanceConfiguration(service_instance_id=service_instance_id,
                                 consumer_params=cpds, pkey=pkey)

if __name__ == "__main__":
    FNAME = ConsumerField(name="name",
                          value="Alfonso Egio",
                          desc="Mi nombre")
    FPICTURE = ConsumerField(name="picture",
                          value="http://example.com/hola.jpg",
                          desc="URL de la foto")
    CP1 = ConsumerParam(path="/var/www/html", fields=[FNAME, FPICTURE])
    CP2 = ConsumerParam(path="/root/chequeo.txt", content="YO ESTUVE AQuÏ")
    IC = InstanceConfiguration(service_instance_id="laksdjlkasjd",
                               consumer_params=[CP1, CP2])
    DB = connect("eroski")
    IC.save()
    IC2 = InstanceConfiguration(service_instance_id="pwoeipqwoei",
                                consumer_params=[CP1, CP2])
    IC2.save()
    for ic in InstanceConfiguration.objects(service_instance_id="pwoeipqwoei"):
        for cpar2 in ic.consumer_params:
            print "\t", cpar2.path
            if 'content' in cpar2:
                print "\t\t", cpar2.content
            if 'fields' in cpar2:
                for f in cpar2.fields:
                    print "\t\t", f.name, "\t=\t", f.value

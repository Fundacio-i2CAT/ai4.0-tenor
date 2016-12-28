#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Instance Configuration model"""

from mongoengine import *
from consumer_param import ConsumerParam,ConsumerField
import datetime

class InstanceConfiguration(Document):
    """Instance configuration class"""

    service_instance_id = StringField(required=True)
    consumer_params = ListField(EmbeddedDocumentField(ConsumerParam))
    timestamp = DateTimeField(default=datetime.datetime.now)

def build_instance_configuration(service_instance_id,consumer_params):
    """Building it from array"""
    cpds = []
    for cp in consumer_params:
        if 'content' in cp:
            cpds.append(ConsumerParam(path=cp['path'], content=cp['content']))
            continue
        if 'fields' in cp:
            fields = []
            for fp in cp['fields']:
                desc = None
                if 'desc' in fp:
                    desc = fp['desc']
                fields.append(ConsumerField(name=fp['name'],
                                            desc=desc,
                                            value=fp['value']))
            cpds.append(ConsumerParam(path=cp['path'], fields=fields))
    return InstanceConfiguration(service_instance_id=service_instance_id,
                                 consumer_params=cpds)

if __name__ == "__main__":
    FNAME = ConsumerField(name="name",
                          value="Alfonso Egio",
                          desc="Mi nombre")
    FPICTURE = ConsumerField(name="picture",
                          value="http://example.com/hola.jpg",
                          desc="URL de la foto")
    CP1 = ConsumerParam(path="/var/www/html", fields=[FNAME,FPICTURE])
    CP2 = ConsumerParam(path="/root/chequeo.txt", content="YO ESTUVE AQuÏ")
    IC = InstanceConfiguration(service_instance_id="laksdjlkasjd",
                               consumer_params=[CP1, CP2])
    DB = connect("eroski")
    IC.save()
    IC2 = InstanceConfiguration(service_instance_id="pwoeipqwoei",
                                consumer_params=[CP1, CP2])
    IC2.save()
    for ic in InstanceConfiguration.objects(service_instance_id="pwoeipqwoei"):
        for cp in ic.consumer_params:
            print "\t", cp.path
            if 'content' in cp:
                print "\t\t", cp.content
            if 'fields' in cp:
                for f in cp.fields:
                    print "\t\t", f.name, "\t=\t", f.value

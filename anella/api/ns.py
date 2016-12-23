#!/usr/bin/python
# -*- coding: utf-8 -*-
"""NS API"""

from tenor_client.tenor_vdu import TenorVDU
from tenor_client.tenor_vnf import TenorVNF
from tenor_client.tenor_ns import TenorNS
from tenor_client.tenor_nsi import TenorNSI
from models.instance_configuration import InstanceConfiguration
from models.instance_configuration import build_instance_configuration

import flask_restful
from flask_restful import abort
from flask import request
import json

class NS(flask_restful.Resource):
    """Network service resources"""
    def __init__(self):
        pass

    def get(self, ns_id=None):
        """Gets NS(s)"""
        ids = TenorNS.get_ns_ids()
        result = []
        if ns_id:
            for nid in ids:
                if nid == ns_id:
                    return {'ns_id': int(nid)}
            abort(404, message='{0} NS not found'.format(ns_id))
        for ns_sid in ids:
            result.append({'ns_id': int(ns_sid)})
        return result

    def delete(self, ns_id):
        """Deletes a NS"""
        vdu = TenorVDU()
        vnf = TenorVNF(vdu)
        tns = TenorNS(vnf)
        tns.set_dummy_id(ns_id)
        try:
            resp = tns.delete()
        except Exception as exc:
            abort(500, message="Error deleting NS: {0}".format(str(exc)))
        if resp.status_code == 200:
            return {'message': 'successfully deleted'}
        else:
            abort(resp.status_code,
                  message='Error deleting {0} ns'.format(ns_id))

    def post(self, ns_id=None):
        """Posts a new NS"""
        if ns_id:
            try:
                data = request.get_json()
                vdu = TenorVDU()
                vnf = TenorVNF(vdu)
                tns = TenorNS(vnf)
                tns.set_dummy_id(ns_id)
                if not 'pop_id' in data:
                    abort(400, message='Lack of PoP id')
                resp = tns.instantiate(data['pop_id'])
                nsdata = json.loads(resp.text)
                icd = build_instance_configuration(nsdata['id'],
                                                   data['context']['consumer_params'])
                icd.save()
                return {'service_instance_id': nsdata['id'],
                        'state': 'PROVISIONED'}
            except:
                nsi = TenorNSI(ns_id)
                nsi.delete()
                abort(500, message='Error instantiating {0}'.format(ns_id))

        data = request.get_json()
        vnf_ids = TenorVNF.get_vnf_ids()
        if not data['vnf_id'] in vnf_ids:
            abort(404, message='vnf_id {0} not found'.format(data['vnf_id']))
        vnf = TenorVNF(data['vnf_id'])
        tns = TenorNS(data['vnf_id'])
        resp = tns.register(data['name'])
        try:
            data = json.loads(resp.text)
        except Exception as exc:
            abort(500,
                  message="Error decoding NS reg.: {0}".format(str(exc)))
        return {'state': 'PROVISIONED', 'ns_id': data['nsd']['id']}

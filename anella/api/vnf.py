#!/usr/bin/python
# -*- coding: utf-8 -*-
"""VNF API"""

from tenor_client.tenor_vdu import TenorVDU
from tenor_client.tenor_vnf import TenorVNF

import flask_restful
from flask_restful import abort
from flask import request
import json

class VNF(flask_restful.Resource):
    """Virtual network function resources"""
    def __init__(self):
        pass

    def delete(self, vnf_id):
        """Deletes a VNF"""
        vnf = TenorVNF(int(vnf_id))
        try:
            vnf.delete()
        except Exception as exc:
            abort(500, message="Error deleting VNF: {0}".format(str(exc)))
        return {'message': 'successfully deleted'}

    def get(self, vnf_id=None):
        """Gets VNF(s)"""
        ids = TenorVNF.get_vnf_ids()
        result = []
        if vnf_id:
            for vid in ids:
                if vid == int(vnf_id):
                    return {'vnf_id': vid}
            abort(404, message='{0} VNF not found'.format(vnf_id))
        for vnf_sid in ids:
            result.append({'vnf_id': vnf_sid})
        return result

    def post(self):
        """Posts a new VNF"""
        data = request.get_json()
        vdu_data = data['vdu']
        cached = "false"
        if 'cached' in vdu_data:
            cached = vdu_data['cached']
        if cached:
            cached = "true"
        vdu = TenorVDU(vdu_data['vm_image'],
                       vdu_data['vm_image_format'],
                       vdu_data['flavor'],
                       cached,
                       vdu_data['shell'],
                       vdu_data['storage_amount'],
                       vdu_data['vcpus'])
        vnf = TenorVNF(vdu)
        try:
            resp = vnf.register(data['name'])
        except Exception as exc:
            abort(500, message="Error registering VNF: {0}".format(str(exc)))
        try:
            data = json.loads(resp.text)
        except Exception as exc:
            abort(500,
                  message="Error decoding VNF reg.: {0}".format(str(exc)))
        return {'state': 'PROVISIONED', 'vnf_id': data['vnfd']['id']}

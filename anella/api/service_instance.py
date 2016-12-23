#!/usr/bin/python
# -*- coding: utf-8 -*-
"""ServiceInstance API"""

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
import ConfigParser

CONFIG = ConfigParser.RawConfigParser()
CONFIG.read('config.cfg')
POP_ID = int(CONFIG.get('tenor', 'default_pop'))

class ServiceInstance(flask_restful.Resource):
    """Service instance resources"""
    def __init__(self):
        pass

    def get(self, ns_id=None):
        """Gets NSI information"""
        try:
            tids = TenorNSI.get_nsi_ids()
        except Exception as exc:
            abort(500,
                  message="Error retrieving NS instances: {0}".format(str(exc)))
        states = []
        for tid in tids:
            nsi = TenorNSI(tid)
            nsi_state = nsi.get_state_and_addresses()
            if ns_id:
                if tid == ns_id:
                    return nsi_state
            else:
                states.append(nsi_state)
        return states

    def post(self):
        """Post a new NSI"""
        data = request.get_json()
        # log_db_client = MongoClient()
        # log_db = log_db_client.orchestrator_logs
        # logs = log_db.logs
        # logs.insert_one({'method': 'POST',
        #                  'request': data,
        #                  'date': datetime.datetime.utcnow()})
        # log_db_client.close()
        context = data['context']
        name = context['name_image']
        cached = "true"
        if 'cached' in context:
            cached = context['cached']
        if cached:
            cached = "true"
        vdu = TenorVDU(context['vm_image'], context['vm_image_format'],
                       context['flavor'], cached)
        if not 'bootstrap_script' in context:
            shell = None
            with open('keys/anella.json') as data_file:
                shell = json.load(data_file)
            context['bootstrap_script'] = shell['shell']
        try:
            vnf = TenorVNF(vdu)
            tns = TenorNS(vnf)
            tns.register(name, context['bootstrap_script'])
            resp = None
            pop_id = POP_ID
            if 'pop_id' in context:
                pop_id = context['pop_id']
            if not 'public_network_id' in context:
                resp = tns.instantiate(pop_id)
            else:
                print context['public_network_id']
                resp = tns.instantiate(pop_id, context['public_network_id'])
            nsdata = json.loads(resp.text)
        except Exception as exc:
            abort(500,
                  message="Error posting NS instance: {0}".format(str(exc)))
        icd = build_instance_configuration(nsdata['id'],
                                           data['context']['consumer_params'])
        icd.save()
        return {'service_instance_id': nsdata['id'], 'state': 'PROVISIONED'}

    def put(self, ns_id=None):
        """Starting/Stopping NSIs"""
        if not ns_id:
            abort(500, message="You should provide a NS id")
        state = request.get_json()
        # log_db_client = MongoClient()
        # log_db = log_db_client.orchestrator_logs
        # logs = log_db.logs
        # logs.insert_one({'method': 'PUT',
        #                  'request': state,
        #                  'date': datetime.datetime.utcnow()})
        # log_db_client.close()
        nsi = TenorNSI(ns_id)
        resp = None
        try:
            if state['state'].upper() == 'START':
                resp = nsi.start()
            if state['state'].upper() == 'STOP':
                resp = nsi.stop()
            if state['state'].upper() == 'RUNNING':
                resp = nsi.start()
            if state['state'].upper() == 'DEPLOYED':
                resp = nsi.stop()
        except Exception as exc:
            abort(500, message='Internal server error: {0}'.format(str(exc)))
        if hasattr(resp, 'status_code'):
            if resp.status_code == 409:
                abort(409,
                      message='Conflict: {0} stopped(running)'.format(ns_id))
            if resp.status_code in (200, 201):
                return {'message': 'Successfully sent state signal',
                        'state': 'UNKNOWN'}
            else:
                abort(404, message='{0} NS not found'.format(ns_id))
        else:
            abort(500,
                  message='Invalid: \'{0}\''.format(state['state'].upper()))

    def delete(self, ns_id):
        """Deletes NSIs"""
        if not ns_id:
            abort(500, message='No instance selected')
        else:
            try:
                nsi = TenorNSI(ns_id)
                nsi.delete()
                msg = '{0} request successfully sent'.format(ns_id)
                return {'message': msg}
            except Exception as exc:
                msg = 'Error deleting NS instance: {0}'.format(str(exc))
                abort(500, message=msg)

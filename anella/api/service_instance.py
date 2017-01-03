#!/usr/bin/python
# -*- coding: utf-8 -*-
"""ServiceInstance API"""

from tenor_client.tenor_vdu import TenorVDU
from tenor_client.tenor_vnf import TenorVNF
from tenor_client.tenor_ns import TenorNS
from tenor_client.tenor_nsi import TenorNSI
from models.instance_configuration import InstanceConfiguration
from models.instance_configuration import build_instance_configuration
from models.tenor_messages import RegularMessage
from models.api_log import ApiLog

from bson import json_util
import flask_restful
from flask_restful import abort
from flask import request
import json
import ConfigParser
from flask import send_file
import uuid
import os
import StringIO

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
        apilog = ApiLog(method='POST', data=request.data)
        apilog.save()
        data = request.get_json()
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
                resp = tns.instantiate(pop_id, context['public_network_id'])
            nsdata = json.loads(resp.text)
        except Exception as exc:
            abort(500,
                  message="Error posting NS instance: {0}".format(str(exc)))
        if resp.status_code == 403:
            edata = json.loads(resp.text)
            abort(403, message=edata['message'])

        icd = build_instance_configuration(nsdata['id'],
                                           data['context']['consumer_params'])
        icd.save()
        return {'service_instance_id': nsdata['id'], 'state': 'PROVISIONED'}

    def put(self, ns_id=None):
        """Starting/Stopping NSIs"""
        apilog = ApiLog(method='PUT', data=request.data)
        apilog.save()
        if not ns_id:
            abort(500, message="You should provide a NS id")
        state = request.get_json()
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

class ServiceInstanceHistory(flask_restful.Resource):
    """Service instance history resources"""
    def __init__(self):
        pass

    def get(self, ns_id):
        """Gets NSI history"""
        events = []
        history = RegularMessage.objects(service_instance_id=ns_id).order_by('timestamp')
        for h in history:
            data = str(h.message)
            info = (data[:75] + '...') if len(data) > 75 else data
            events.append({'time': str(h.timestamp), 'message': info,
                           'severity': str(h.severity)})
        return events

class ServiceInstanceKey(flask_restful.Resource):
    """Service instance history resources"""
    def __init__(self):
        pass

    def get(self, ns_id):
        """Gets a new service instance key"""
        nsi = TenorNSI(ns_id)
        private_key = nsi.create_provider_key()
        filename = uuid.uuid4()
        strIO = StringIO.StringIO()
        strIO.write(private_key)
        strIO.seek(0)
        # fake filename to avoid keeping the provider's private key
        #    in the plataforma 4.0 host system
        private_filename = '/tmp/{0}.pem'.format(filename)
        return send_file(strIO,
                         attachment_filename=private_filename,
                         as_attachment=True)

#!/usr/bin/python
# -*- coding: utf-8 -*-
"""ServiceInstance API"""

import flask_restful
from flask_restful import abort
from flask import request
import json
import ConfigParser
from flask import send_file
import uuid
import StringIO
from time import mktime, strptime, strftime
from datetime import datetime
from pprint import pprint
from datetime import datetime, timedelta
from Crypto.PublicKey import RSA
from bson import json_util
from models.monitoring_mockup import MonitoringMockup
from models.instance_mockup import InstanceMockup

CONFIG = ConfigParser.RawConfigParser()
CONFIG.read('config.cfg')

class ServiceInstance(flask_restful.Resource):
    """Service instance resources"""
    def __init__(self):
        pass

    def retrieve_state_and_addresses(self, ns_id):
        instance = InstanceMockup.objects(service_instance_id=ns_id)
        state_and_addresses = {
            "addresses": [
                {
                    "OS-EXT-IPS:type": "fixed",
                    "addr": "192.222.206.4"
                },
                {
                    "OS-EXT-IPS:type": "floating",
                    "addr": "87.236.219.29"
                }
            ],
            "image_path": "zesty-server-cloudimg-amd64.img",
            "runtime_params": [
                {
                    "desc": "Service instance IP address",
                    "name": "floating_ip",
                    "value": "87.236.219.29"
                }
            ],
            "service_instance_id": instance[0].service_instance_id,
            "state": instance[0].state
        }
        if instance[0].state == 'PROVISIONED':
            instance[0].update(state='UNKNOWN')
            return state_and_addresses
        if instance[0].state == 'UNKNOWN':
            instance[0].update(state='RUNNING')
            mmo = MonitoringMockup(service_instance_id=instance[0].service_instance_id,
                                   message='ACTIVE')
            mmo.save()
        return state_and_addresses

    def get(self, ns_id=None):
        """Gets NSI information"""
        tids = [x.service_instance_id for x in InstanceMockup.objects()]
        if ns_id:
            for tid in tids:
                print tid
                print ns_id
                if tid == ns_id:
                    return self.retrieve_state_and_addresses(tid)
        if ns_id:
            abort(404)
        instances = []
        for tid in tids:
            instances.append(self.retrieve_state_and_addresses(tid))
        return instances

    def post(self):
        """Post a new NSI"""
        ssid = str(uuid.uuid4())
        state = 'PROVISIONED'
        inst = InstanceMockup(service_instance_id=ssid,
                              state='PROVISIONED')
        inst.save()
        return {'service_instance_id': ssid, 'state': state}

    def put(self, ns_id=None):
        """Starting/Stopping NSIs"""
        if not ns_id:
            abort(500, message="You should provide a NS id")
        instance = InstanceMockup.objects(service_instance_id=ns_id)
        if len(instance) == 0:
            abort(404)
        state = request.get_json()
        
        resp = None
        if state['state'].upper() == 'RUNNING':
            if instance[0].state == 'RUNNING':
                abort(409, code='START_STOP_CONFLICT', state='RUNNING')
            else:
                mmo = MonitoringMockup(service_instance_id=ns_id, message='ACTIVE')
                mmo.save()
                instance[0].update(state='RUNNING')
                return {'state': 'RUNNING'}
        if state['state'].upper() == 'DEPLOYED':
            if instance[0].state == 'DEPLOYED':
                abort(409, code='START_STOP_CONFLICT', state='DEPLOYED')
            else:
                mmo = MonitoringMockup(service_instance_id=ns_id, message='SHUTOFF')
                mmo.save()
                instance[0].update(state='DEPLOYED')
                return {'state': 'DEPLOYED'}
            
        if state['state'].upper() == 'DENIED':
            instance[0].update(state='DENIED')
            if instance[0].state == 'DEPLOYED':
                abort(409, code='START_STOP_CONFLICT', state='DENIED')
            else:
                instance[0].update(state='DENIED')
                mmo = MonitoringMockup(service_instance_id=ns_id, message='DEPLOYED')
                mmo.save()
                return {'state': 'DENIED'}

    def delete(self, ns_id=None):
        """Deletes NSIs"""
        if ns_id:
            instances = InstanceMockup.objects(service_instance_id=ns_id)
        else:
            instances = InstanceMockup.objects()
        for inst in instances:
            inst.delete()
            mmo = MonitoringMockup(service_instance_id=inst.service_instance_id, message='DELETE_REQUEST_RECEIVED')
            mmo.save()

        return {'message': 'Delete request OK'}

def monitoring_events(ns_id,idate, fdate=None):
        initial_date = datetime.fromtimestamp(mktime(strptime(idate, '%Y-%m-%d')))
        final_date = None
        checkInstance = MonitoringMockup.objects(service_instance_id=ns_id)
        if len(checkInstance) == 0:
            abort(404, message="Service instance {0} monitoring not found".format(ns_id))
        if fdate:
            final_date = datetime.fromtimestamp(mktime(strptime(fdate, '%Y-%m-%d')))
        monitoring = []
        if final_date == None:
            monitoring = MonitoringMockup.objects(service_instance_id=ns_id,
                                                   timestamp__gte=initial_date).order_by('timestamp')
        else:
            monitoring = MonitoringMockup.objects(service_instance_id=ns_id,
                                                   timestamp__gte=initial_date,
                                                   timestamp__lt=final_date).order_by('timestamp')
        return monitoring, initial_date, final_date

class ServiceInstanceMonitoring(flask_restful.Resource):
    """Service instance monitoring resources"""
    def __init__(self):
        pass

    def get(self, ns_id, idate, fdate=None):
        """Gets NSI monitoring"""
        monitoring, initial_date, final_date = monitoring_events(ns_id, idate, fdate)
        hours_acum = 0
        active_flag = False
        last_active_time = initial_date
        events = []
        for mev in monitoring:
            data = str(mev.message)
            info = (data[:75] + '...') if len(data) > 75 else data
            if data.upper() == 'ACTIVE':

                pass
            events.append({'time': str(mev.timestamp), 'message': info})
        if len(events) > 0:
            return events
        else:
            abort(404, message="Service instance {0} history not found".format(ns_id))


class ServiceInstanceBilling(flask_restful.Resource):
    """Service instance history resources"""
    def __init__(self):
        pass

    def get(self, ns_id, idate, fdate=None):
        """Get the time difference between an activation and a termination event or current time"""
        monitoring, initial_date, final_date = monitoring_events(ns_id, idate, fdate)
        first_slot = True
        last_active = None
        time_acum = timedelta(minutes=0)
        lapses = []

        activation = MonitoringMockup.objects(service_instance_id=ns_id, message='ACTIVE')
        if len(activation) == 0:
            resp = {'lapses': [], 'total_minutes': 0, 'total_delta': None}
            return resp

        for mev in monitoring:
            if (mev['message'].upper() == 'SHUTOFF') or (mev['message'].upper() == 'DELETE_REQUEST_RECEIVED'):
                if first_slot == True:
                    dt = mev['timestamp']-initial_date
                    time_acum += dt
                    lapses.append({'t0': initial_date.strftime('%d-%m-%Y %H:%M:%S'),
                                   't1': mev['timestamp'].strftime('%d-%m-%Y %H:%M:%S'),
                                   'delta': str(dt)})
            if last_active and mev['message'] != 'ACTIVE':
                dt =  mev['timestamp']-last_active
                time_acum += dt
                lapses.append({'t0': last_active.strftime('%d-%m-%Y %H:%M:%S'),
                               't1': mev['timestamp'].strftime('%d-%m-%Y %H:%M:%S'),
                               'delta': str(dt)})
            first_slot = False
            if mev['message'].upper() == 'ACTIVE':
                last_active = mev['timestamp']
        if len(monitoring) > 0:
            if monitoring[len(monitoring)-1]['message'] == 'ACTIVE':
                now = datetime.now()
                dt = now-monitoring[len(monitoring)-1]['timestamp']
                time_acum += dt
                lapses.append({'t0': monitoring[len(monitoring)-1]['timestamp'].strftime('%d-%m-%Y %H:%M:%S'),
                               't1': now.strftime('%d-%m-%Y %H:%M:%S'),
                               'delta': str(dt)})
        resp = {'lapses': lapses, 'total_minutes': int(time_acum.total_seconds()/60.0)+1, 'total_delta': str(time_acum)}
        return resp

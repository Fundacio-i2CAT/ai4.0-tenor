#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Log API"""

from tenor_client.tenor_nsi import TenorNSI
from tenor_client.callback import Callback
from models.tenor_messages import CriticalError
from models.tenor_messages import MonitoringMessage
from models.tenor_messages import FirstBoot
from models.instance_snapshot import InstanceSnapshot

import re
import flask_restful
from flask import request

class Log(flask_restful.Resource):
    """TeNOR Logs"""
    def __init__(self):
        pass

    def post(self):
        """Log post"""
        data = request.get_json()

        if 'descriptor_reference' in data:
            ns_instance_id = data['id']
            monim = MonitoringMessage(service_instance_id=ns_instance_id,
                                      message='ACTIVE')
            monim.save()
            nsi = TenorNSI(ns_instance_id)
            nsi.configure()
            fbm = FirstBoot(service_instance_id=ns_instance_id,
                            message='FIRST_BOOT')
            fbm.save()
            nsi.stop()

        if 'status' in data:
            print data['status']
            message = ''
            if 'message' in data:
                print data['message']
                message = data['message']
            if str(data['status']) == 'error':
                code = ''
                if 'code' in data:
                    code = data['code']
                    if code == 'ERROR_CREATING_INSTANCE':
                        if re.search('disk is too small', message):
                            code = 'FLAVOR_TOO_SMALL'
                crite = CriticalError(service_instance_id=data['service_instance_id'],
                                      message=message, code=code)
                crite.save()

        if 'state_change' in data:
            fbms = FirstBoot.objects(service_instance_id=data['service_instance_id'])
            if len(fbms) > 0:
                if data['state_change']['reached'] == 'ACTIVE':
                    FirstBoot.objects(service_instance_id=data['service_instance_id']).delete()
                    nsi = TenorNSI(data['service_instance_id'])
                    to_service_manager = nsi.get_state_and_addresses()
                    Callback(to_service_manager)
                else:
                    nsi = TenorNSI(data['service_instance_id'])
                    nsi.start()
            else:
                monim = MonitoringMessage(service_instance_id=data['service_instance_id'],
                                          message=data['state_change']['reached'])
                monim.save()

        if 'snapshot' in data:
            print data['snapshot']
            inssnp = InstanceSnapshot(service_instance_id=data['service_instance_id'],
                                      image_id=data['snapshot']['image_id'],
                                      name_image=data['snapshot']['name_image'])
            inssnp.save()

    def get(self):
        """Log get"""
        return 200

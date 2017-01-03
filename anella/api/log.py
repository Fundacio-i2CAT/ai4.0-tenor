#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Log API"""

from tenor_client.tenor_nsi import TenorNSI
from tenor_client.callback import Callback
from models.tenor_messages import CriticalError

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
            nsi = TenorNSI(ns_instance_id)
            nsi.configure()
            try:
                to_service_manager = nsi.get_state_and_addresses()
                Callback(to_service_manager)
            except:
                pass

        if 'status' in data:
            print data['status']
            message = ''
            if 'message' in data:
                print data['message']
                message = data['message']
            if str(data['status']) == 'error':
                crite = CriticalError(service_instance_id=data['service_instance_id'],
                                      message=message)
                crite.save()

    def get(self):
        """Log get"""
        return 200

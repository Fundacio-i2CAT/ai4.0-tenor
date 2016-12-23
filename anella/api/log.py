#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Log API"""

from tenor_client.tenor_ns import TenorNS
from tenor_client.tenor_nsi import TenorNSI
from tenor_client.tenor_vnf import TenorVNF
from tenor_client.tenor_vdu import TenorVDU
from tenor_client.callback import Callback

import flask_restful
from flask_restful import abort
from flask import request
import json

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
                callback = Callback(to_service_manager)
            except:
                pass

        # if 'status' in data:
            # try:
            #     # if data['status'] == 'error':
            #         # log_db_client = MongoClient()
            #         # log_db = log_db_client.orchestrator_logs
            #         # errors = log_db.errors
            #         # errors.insert_one({'method': 'POST',
            #         #                    'service_instance_id': data['service_instance_id'],
            #         #                    'date': datetime.datetime.utcnow()})
            #         # log_db_client.close()
            # except:
            #     pass

    def get(self):
        """Log get"""
        return 200

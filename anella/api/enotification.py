#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Enotification API"""

import flask_restful
from flask import request
from models.tenor_messages import RegularMessage

class Enotification(flask_restful.Resource):
    """TeNOR error management"""
    def __init__(self):
        pass

    def post(self):
        """Log post"""
        data = request.get_json()
        if 'op_id' in data:
            if type(data['op_id']) is unicode:
                if 'msg' in data:
                    if (type(data['msg']) is unicode) or (type(data['msg']) is str):
                        regm = RegularMessage(service_instance_id=data['op_id'],
                                              message=data['msg'],
                                              module=data['module'],
                                              severity=data['severity'])
                        regm.save()

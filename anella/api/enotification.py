#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Enotification API"""

import flask_restful
from flask_restful import abort
from flask import request
from models.tenor_messages import RegularMessage
import json

class Enotification(flask_restful.Resource):
    """TeNOR error management"""
    def __init__(self):
        pass

    def post(self):
        """Log post"""
        data1 = request.get_json()
        print "ENOTIFICATION ENDPOINT INFO"
	print data1
        if 'op_id' in data1:
            if type(data1['op_id']) is unicode:
                regm = RegularMessage(service_instance_id=data1['op_id'],
                                      message=data1['msg'],
                                      module=data1['module'],
                                      severity=data1['severity'])
                regm.save()

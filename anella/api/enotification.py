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
        data = request.get_json()
        print "ENOTIFICATION ENDPOINT INFO"
	print data
        if 'op_id' in data:
            if type(data['op_id']) is unicode:
                regm = RegularMessage(service_instance_id=data['op_id'],
                                      message=data['msg'],
                                      module=data['module'],
                                      severity=data['severity'])
                regm.save()

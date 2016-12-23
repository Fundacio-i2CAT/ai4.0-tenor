#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Enotification API"""

import flask_restful
from flask_restful import abort
from flask import request
import json

class Enotification(flask_restful.Resource):
    """TeNOR error management"""
    def __init__(self):
        pass

    def post(self):
        """Log post"""
        data1 = request.get_json()
	# print data1
        if 'severity' in data1:
            if data1['severity'].upper() == 'ERROR':
                pass
                # print "ERROR =>"
                # print data1['msg']
                # print "ERROR =>"

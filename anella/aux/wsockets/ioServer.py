#!/usr/bin/python
# -*- coding: utf-8 -*-

import flask_restful
from flask import Flask, Blueprint, request, session, render_template
from flask_restful import Api, abort
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO
import os
import requests
import json
from flask_socketio import SocketIO, emit, disconnect

URL_PREFIX = ''
HOST = '0.0.0.0'
PORT = 6062
API_V2_BP = Blueprint('api_v1', __name__)
API_V2 = Api(API_V2_BP)
APP = Flask(__name__)
APP.config['SECRET_KEY'] = 'secret!'
SOCKETIO = SocketIO(APP, async_mode=None)

ORCHESTRATOR_URL = 'http://localhost:8082/orchestrator/api/v0.1/service/instance'

@APP.route('/')
def index():
    return render_template('own.html', async_mode=SOCKETIO.async_mode)

# class Launch(flask_restful.Resource):
#     def post(self):
#         data = request.get_json()
#         response = requests.post(ORCHESTRATOR_URL,
#                                  headers={'Content-Type': 'application/json'},
#                                  json=data)
#         resp = json.loads(response.text)
#         print resp['service_instance_id']
#         return 200


@SOCKETIO.on('my_event')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    print "LKJASDLKJASD"
    # emit('my_response',
    #      {'data': message['data'], 'count': session['receive_count']})

# API_V2.add_resource(Launch,'/launch')

if __name__ == "__main__":
    print "IO server"
    # APP.register_blueprint(
    #     API_V2_BP,
    #     url_prefix=URL_PREFIX
    # )
    SOCKETIO.run(APP, debug=True)

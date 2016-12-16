#!/usr/bin/python
# -*- coding: utf-8 -*-

import flask_restful
from flask import Flask, Blueprint, request, session, render_template
from flask import send_from_directory
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

@APP.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('static', path)

@SOCKETIO.on('my_event')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    print message['data']
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})

if __name__ == "__main__":
    print "IO server"
    SOCKETIO.run(APP, debug=True)


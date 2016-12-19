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
from pymongo import MongoClient

ADAM_EXAMPLE = {
    "context" : {
	"runtime_params" : [
            {
		"name" : "wwwwww",
		"desc" : "sssssss"
            }
	],
        "callback_url": "http://localhost:5000/callback",
	"public_network_id" : "71257860-3085-40bb-b009-5f12c688cdfb",
	"name_image" : "LuNESs",
	"pop_id": 21,
        "vm_image_format" : "openstack_id",
	"tenor_url" : "http://localhost:4000",
	"vm_image" : "5d4fdb85-3e7a-4e92-be67-72214a61275d",
	"flavor" : "VM.M1",
	"consumer_params" : [
            {
		"path" : "/var/www/html/index.html",
		"fields" : [
                    {
			"required" : True,
			"name" : "name",
			"desc" : "Name of the consumer",
			"value" : "Example deployment"
                    },
                    {
			"required" : True,
			"name" : "picture",
			"desc" : "Consumer server Picture",
			"value" : "https://dimoniko.files.wordpress.com/2011/01/hora-de-aventura.jpg"
                    },
                    {
			"required" : True,
			"name" : "cv",
			"desc" : "CV del consumer",
			"value" : "laksjd laksdj laksjd laks jdlkas jdlkas jd"
                    }
		]
            },
            {
		"path" : "/root/chequeo.txt",
		"content" : "YO ESTUVE AQUI"
	    }
	]
    }
}

URL_PREFIX = ''
HOST = '0.0.0.0'
PORT = 6062
API_V2_BP = Blueprint('api_v1', __name__)
API_V2 = Api(API_V2_BP)
APP = Flask(__name__)
APP.config['SECRET_KEY'] = 'secret!'
SOCKETIO = SocketIO(APP, async_mode=None)

ORCHESTRATOR_URL = 'http://localhost:8082/orchestrator/api/v0.1'

CLIENTS = []

def test_08(name_image, name, picture, cv):
    """Posts service/instance one round mode at Adam with fixed network/pop"""
    url = '{0}/service/instance'.format(ORCHESTRATOR_URL)
    aexample = ADAM_EXAMPLE
    aexample['context']['name_image'] = name_image
    for config in aexample['context']['consumer_params']:
        if 'fields' in config:
            for cp in config['fields']:
                if cp['name'] == 'name':
                    cp['value'] = name
                if cp['name'] == 'picture':
                    cp['value'] = picture
                if cp['name'] == 'cv':
                    cp['value'] = cv
    print url
    resp = requests.post(url, headers={'Content-Type': 'application/json'},
                         json=aexample)
    response = json.loads(resp.text)
    print response
    print response['service_instance_id']
    return response['service_instance_id']

@APP.route('/')
def index():
    return render_template('own.html', async_mode=SOCKETIO.async_mode)

@APP.route('/callback', methods=['POST'])
def callback():
    cbData = request.get_json()
    print cbData['id']
    client = MongoClient()
    mdb = client.wsockets
    client_ids = mdb.client_ids
    client_id = client_ids.find_one({'service_instance_id': cbData['id']})
    print client_id
    SOCKETIO.emit('running', {'msg': cbData['id']}, room=client_id['client_sid'])
    client.close()
    return ""

@APP.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('static', path)

@SOCKETIO.on('connected')
def connected():
    print "{0} connected".format(request.sid)
    CLIENTS.append(request.namespace)

@SOCKETIO.on('disconnect')
def disconnect():
    print "{0} disconnected".format(request.sid)
    CLIENTS.remove(request.namespace)

@SOCKETIO.on('launch')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    print "LAUNCH COMMAND RECEIVED"
    print "SID"
    print request.sid
    print message['data']
    service_instance_id = test_08(message['data']['name_image'],
                                  message['data']['name'],
                                  message['data']['picture'],
                                  message['data']['cv'])
    client = MongoClient()
    mdb = client.wsockets
    client_ids = mdb.client_ids
    client_ids.insert_one({'service_instance_id': service_instance_id,
                           'client_sid': request.sid})
    client.close()



if __name__ == "__main__":
    print "IO server"
    SOCKETIO.run(APP, debug=True)

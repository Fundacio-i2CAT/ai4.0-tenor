#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Anella 4.0 Orchestrator"""

from flask import Flask, Blueprint
from flask_restful import Api
import ConfigParser
from flask_mongoengine import MongoEngine
from api.service_instance import ServiceInstance
from api.service_instance import ServiceInstanceBilling

CONFIG = ConfigParser.RawConfigParser()
CONFIG.read('config.cfg')

HOST = CONFIG.get('flask', 'host')
PREFIX = CONFIG.get('flask', 'prefix')
API_VERSION = CONFIG.get('flask', 'version')
PORT = int(CONFIG.get('flask', 'port'))
APP = Flask(__name__)
API_V2_BP = Blueprint('api_v2', __name__)
API_V2 = Api(API_V2_BP)
URL_PREFIX = '{prefix}/v{version}'.format(
    prefix=PREFIX,
    version=API_VERSION)
BASE_URL = 'http://localhost:{0}{1}'.format(PORT, URL_PREFIX)

API_V2.add_resource(ServiceInstance,
                    '/service/instance',
                    '/service/instance/<ns_id>',
                    '/service/instance/<ns_id>/state')

API_V2.add_resource(ServiceInstanceBilling,
                    '/service/instance/<ns_id>/billing/<idate>',
                    '/service/instance/<ns_id>/billing/<idate>/<fdate>')

APP.register_blueprint(
    API_V2_BP,
    url_prefix=URL_PREFIX
)

APP.config['MONGODB_SETTINGS'] = {'db': CONFIG.get('mongodb', 'database')}
DB = MongoEngine()
DB.init_app(APP)

if __name__ == "__main__":
    print "Industrial Platform 4.0 Orchestrator"
    APP.run(debug=True, host=HOST, port=PORT, threaded=True)

#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Anella 4.0 Orchestrator"""

from api.pop import PoP, IsCached
from api.vnf import VNF
from api.ns import NS
from api.service_instance import ServiceInstance
from api.service_instance import ServiceInstanceHistory
from api.service_instance import ServiceInstanceMonitoring
from api.service_instance import ServiceInstanceBilling
from api.service_instance import ServiceInstanceKey
from api.service_instance import ServiceInstanceSnapshot
from api.log import Log
from api.enotification import Enotification

from flask import Flask, Blueprint
from flask_restful import Api
import ConfigParser
from flask_mongoengine import MongoEngine

CONFIG = ConfigParser.RawConfigParser()
CONFIG.read('config.cfg')
POP_ID = int(CONFIG.get('tenor', 'default_pop'))

HOST = CONFIG.get('flask', 'host')
PREFIX = CONFIG.get('flask', 'prefix')
API_VERSION = CONFIG.get('flask', 'version')
PORT = int(CONFIG.get('flask', 'port'))
APP = Flask(__name__)
API_V2_BP = Blueprint('api_v2', __name__)
API_V2 = Api(API_V2_BP)
DEFAULT_TENOR_URL = format('{0}:{1}'.format(
    CONFIG.get('tenor', 'url'),
    CONFIG.get('tenor', 'port')))
URL_PREFIX = '{prefix}/v{version}'.format(
    prefix=PREFIX,
    version=API_VERSION)
BASE_URL = 'http://localhost:{0}{1}'.format(PORT, URL_PREFIX)

API_V2.add_resource(Log, '/log')

API_V2.add_resource(Enotification, '/enotification')

API_V2.add_resource(ServiceInstance,
                    '/service/instance',
                    '/service/instance/<ns_id>',
                    '/service/instance/<ns_id>/state')

API_V2.add_resource(ServiceInstanceHistory,
                    '/service/instance/<ns_id>/history')

API_V2.add_resource(ServiceInstanceMonitoring,
                    '/service/instance/<ns_id>/monitoring/<idate>',
                    '/service/instance/<ns_id>/monitoring/<idate>/<fdate>')

API_V2.add_resource(ServiceInstanceBilling,
                    '/service/instance/<ns_id>/billing/<idate>',
                    '/service/instance/<ns_id>/billing/<idate>/<fdate>')

API_V2.add_resource(ServiceInstanceKey,
                    '/service/instance/<ns_id>/key')

API_V2.add_resource(ServiceInstanceSnapshot,
                    '/service/instance/<ns_id>/snapshot')

API_V2.add_resource(VNF,
                    '/vnf',
                    '/vnf/<vnf_id>')

API_V2.add_resource(NS,
                    '/ns',
                    '/ns/<ns_id>')

API_V2.add_resource(PoP,
                    '/pop',
                    '/pop/<pop_id>',
                    '/pop/<pop_id>/<resource>')

API_V2.add_resource(IsCached,
                    '/iscached',
                    '/iscached/<pop_id>')

APP.register_blueprint(
    API_V2_BP,
    url_prefix=URL_PREFIX
)

APP.config['MONGODB_SETTINGS'] = {'db': 'pi40orch'}
DB = MongoEngine()
DB.init_app(APP)

if __name__ == "__main__":
    print "Industrial Platform 4.0 Orchestrator"
    APP.run(debug=False, host=HOST, port=PORT, threaded=True)

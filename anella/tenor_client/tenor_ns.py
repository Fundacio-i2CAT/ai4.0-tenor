#!/usr/bin/python
# -*- coding: utf-8 -*-
"""TeNOR Network Service Representation Class and Client"""

import requests
import json
from jinja2 import Template
from tenor_dummy_id import TenorDummyId
from tenor_vnf import TenorVNF
from tenor_vdu import TenorVDU
from tenor_pop import TenorPoP

import ConfigParser

CONFIG = ConfigParser.RawConfigParser()
CONFIG.read('config.cfg')

POP_ID = int(CONFIG.get('tenor', 'default_pop'))
DEFAULT_TENOR_URL = format('{0}:{1}'.format(
    CONFIG.get('tenor', 'url'),
    CONFIG.get('tenor', 'port')))

DEFAULT_TEMPLATE = './tenor_client/templates/simple-f.json'
DEFAULT_CALLBACK_URL = 'http://localhost:8082/orchestrator/api/v0.1/log'
DEFAULT_TEMPLATE = './tenor_client/templates/simple-n.json'
DEFAULT_FLAVOR = 'basic'

class TenorNS(object):
    """Represents a TeNOR NS"""
    def __init__(self, vnf,
                 tenor_url=DEFAULT_TENOR_URL,
                 template=DEFAULT_TEMPLATE):
        self._template = template
        self._tenor_url = tenor_url
        self._dummy_id = None
        self._lite = False
        if type(vnf) is int:
            self._vnf = TenorVNF(vnf)
            self._lite = True
        else:
            self._vnf = vnf
        self._nsd = None

    def delete(self):
        """Deletes the NS"""
        url = '{0}/network-services/{1}'.format(self._tenor_url,
                                                self._dummy_id)
        try:
            resp = requests.delete(url)
        except:
            raise IOError('{0} instance unreachable'.format(self._tenor_url))
        return resp

    def get_last_ns_id(self):
        """Gets last ns_id"""
        try:
            resp = requests.get('{0}/network-services'.format(self._tenor_url))
        except:
            raise IOError('{0} instance unreachable'.format(self._tenor_url))
        try:
            nss = json.loads(resp.text)
        except:
            raise ValueError('Decoding last_ns_id json resp failed')
        ids = sorted([x['nsd']['id'] for x in nss])
        if len(ids) == 0:
            return TenorDummyId(1898)
        return TenorDummyId(ids[-1])

    def register(self, name, bootstrap_script=None):
        """Registers a NS via TeNOR"""
        self._dummy_id = self.get_last_ns_id()+1
        if self._lite == False:
            if not bootstrap_script:
                self._vnf.register(name,
                                   bootstrap_script=self._vnf.get_vdu().shell)
            else:
                self._vnf.register(name, bootstrap_script)
        try:
            with open(self._template, 'r') as fhandle:
                templ = Template(fhandle.read())
        except:
            raise IOError('Template {0} IOError'.format(self._template))
        resp = None
        while (resp == None) or (not resp.status_code in (200,201)):
            self._nsd = templ.render(ns_id=self._dummy_id,
                                     vnf_id=self._vnf.get_dummy_id(),
                                     flavor=self._vnf.get_vdu().flavor,
                                     name=name)
            try:
                resp = requests.post('{0}/network-services'.format(self._tenor_url),
                                     headers={'Content-Type': 'application/json'},
                                     json=json.loads(self._nsd))
                if resp.status_code == 409:
                    self._dummy_id = str(int(self._dummy_id)+1)
            except IOError:
                raise IOError('{0} instance unreachable'.format(self._tenor_url))
        try:
            json.loads(resp.text)
        except:
            raise ValueError('Decoding new NS resp json resp failed')
        return resp

    def instantiate(self,
                    pop_id=None,
                    public_network_id=None,
                    callback_url=DEFAULT_CALLBACK_URL,
                    flavor=None):
        """Instantiates the NS on openstack"""
        vdu = self._vnf.get_vdu()
        if vdu.flavor:
            flavor = vdu.flavor
        else:
            flavor = DEFAULT_FLAVOR
        ns_data = {'ns_id': self._dummy_id, 'pop_id': pop_id,
                   'callbackUrl': callback_url, 'flavour': flavor,
                   'public_network_id': public_network_id}
        quota = self.check_quota(pop_id, flavor)
        if quota:
            resp = type('',(object,),{'text': json.dumps({"message": quota}),
                                      'status_code': 403})()
            return resp
        try:
            resp = requests.post('{0}/ns-instances'.format(self._tenor_url),
                                 headers={'Content-Type': 'application/json'},
                                 json=ns_data)
        except IOError:
            raise IOError('{0} instance unreachable'.format(self._tenor_url))
        except ValueError:
            raise ValueError('Json encoding error instantiating NS')
        try:
            json.loads(resp.text)
        except:
            raise ValueError('Decoding new NSI resp json resp failed')
        return resp

    def check_quota(self, pop_id, flavor):
        """Check resource quotas on the VIM"""
        if not pop_id:
            pop_id = POP_ID
        pop = TenorPoP(pop_id)
        flavors_available = pop.get_flavor_details()
        target_flavor = None
        value = None
        for flava in flavors_available:
            if flava['name'] == flavor:
                target_flavor = flava
        ram = pop.get_ram_details()
        if target_flavor:
            if target_flavor['ram']+ram['used'] > ram['quota']:
                value = 'ram quota limit reached'
        cores = pop.get_core_details()
        if target_flavor:
            if target_flavor['vcpus']+cores['used'] > cores['quota']:
                value = 'core quota limit reached'
        floating_ips = pop.get_floating_ip_details()
        # The +1 below should be +some_variable in services
        #               requiring more than one floating_ip
        if floating_ips['used']+1 > floating_ips['quota']:
            value = 'floating ips limit reached'
        return value

    def set_dummy_id(self, dummy_id):
        """Sets dummy_id"""
        self._dummy_id = dummy_id

    @staticmethod
    def get_ns_ids():
        """Returns the list of NS registered in TeNOR"""
        url = '{0}/network-services'.format(DEFAULT_TENOR_URL)
        try:
            resp = requests.get(url)
        except:
            raise IOError('{0} instance unreachable'.format(DEFAULT_TENOR_URL))
        try:
            json.loads(resp.text)
        except:
            raise ValueError('Decoding NS response json response failed')
        ids = []
        for tns in json.loads(resp.text):
            ids.append(tns['nsd']['id'])
        return ids


if __name__ == "__main__":
    VDU = TenorVDU()
    VNF = TenorVNF(VDU)
    NS = TenorNS(VNF)
    print NS.get_last_ns_id()
    print NS.register("Test")
    NS.delete()

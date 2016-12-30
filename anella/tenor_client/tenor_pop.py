#!/usr/bin/python
# -*- coding: utf-8 -*-
"""TeNOR PoP Class"""

import requests
import json

DEFAULT_TENOR_URL = 'http://localhost:4000'

class TenorPoP(object):
    """Represents a TeNOR PoP"""

    def __init__(self, pop_id=None, tenor_url=DEFAULT_TENOR_URL):
        self._pop_id = int(pop_id)

    def get_name(self):
        url = '{0}/pops/dc/{1}'.format(DEFAULT_TENOR_URL,self._pop_id)
        try:
            resp = requests.get(url)
        except:
            raise IOError('{0} instance unreachable'.format(DEFAULT_TENOR_URL))
        try:
            json.loads(resp.text)
        except:
            raise ValueError('Decoding PoP response json response failed')
        ids = []
        pop = json.loads(resp.text)
        return pop['name']

    def get_server_details(self):
        url = '{0}/pops/servers/{1}'.format(DEFAULT_TENOR_URL,self._pop_id)
        try:
            resp = requests.get(url)
        except:
            raise IOError('{0} PoP unreachable'.format(self._pop_id))
        try:
            servers = json.loads(resp.text)
        except:
            raise ValueError('Decoding PoP response json response failed')
        return servers['servers']

    def get_quota_details(self):
        url = '{0}/pops/quotas/{1}'.format(DEFAULT_TENOR_URL,self._pop_id)
        try:
            resp = requests.get(url)
        except:
            raise IOError('{0} PoP unreachable'.format(self._pop_id))
        try:
            quotas = json.loads(resp.text)
        except:
            raise ValueError('Decoding PoP response json response failed')
        return quotas['quota_set']

    def get_network_details(self):
        url = '{0}/pops/networks/{1}'.format(DEFAULT_TENOR_URL,self._pop_id)
        try:
            resp = requests.get(url)
        except:
            raise IOError('{0} PoP unreachable'.format(self._pop_id))
        try:
            networks = json.loads(resp.text)
        except:
            raise ValueError('Decoding PoP response json response failed')
        network_details = []
        for network in networks["networks"]:
            network_details.append({'name': network['name'],
                                   'id': network['id'],
                                   'router_external': network['router:external']})
        return network_details

    def get_floating_ip_details(self):
        servers = self.get_server_details()
        quota = self.get_quota_details()
        floating_ips = int(quota['floating_ips'])
        used_floating_ips = 0
        for server in servers:
            for key in server['addresses'].keys():
                for address in server['addresses'][key]:
                    if address['OS-EXT-IPS:type'].upper() == 'FLOATING':
                        used_floating_ips = used_floating_ips+1
        return {'quota': floating_ips, 'used': used_floating_ips, 'ratio': float(used_floating_ips)/float(floating_ips)}

    def get_core_details(self):
        servers = self.get_server_details()
        quota = self.get_quota_details()
        cores = int(quota['cores'])
        used_cores = 0
        for server in servers:
            if server['status'].upper() == 'ACTIVE':
                used_cores = used_cores+int(server['flavor']['detail']['vcpus'])
        return {'quota': cores, 'used': used_cores, 'ratio': float(used_cores)/float(cores)}

    def get_ram_details(self):
        servers = self.get_server_details()
        quota = self.get_quota_details()
        ram = int(quota['ram'])
        used_ram = 0
        for server in servers:
            if server['status'].upper() == 'ACTIVE':
                used_ram = used_ram+int(server['flavor']['detail']['ram'])
        return {'quota': ram, 'used': used_ram, 'ratio': float(used_ram)/float(ram),
                'units': 'MB'}

    def get_flavor_details(self):
        url = '{0}/pops/flavours/{1}'.format(DEFAULT_TENOR_URL,self._pop_id)
        try:
            resp = requests.get(url)
        except:
            raise IOError('{0} PoP unreachable'.format(self._pop_id))
        try:
            flavors = json.loads(resp.text)
        except:
            raise ValueError('Decoding PoP response json response failed')
        flavor_details = []
        for flavor in flavors["flavors"]:
            flavor_details.append({'name': flavor['name'],
                                   'ram': flavor['ram'],
                                   'disk': flavor['disk'],
                                   'vcpus': flavor['vcpus']})
        return flavor_details

    @staticmethod
    def get_pop_ids():
        """Gets the list of PoP registered"""
        url = '{0}/pops/dc'.format(DEFAULT_TENOR_URL)
        try:
            resp = requests.get(url)
        except:
            raise IOError('{0} instance unreachable'.format(DEFAULT_TENOR_URL))
        try:
            json.loads(resp.text)
        except:
            raise ValueError('Decoding PoP response json response failed')
        ids = []
        for pop in json.loads(resp.text):
            ids.append(int(pop['id']))
        return ids

if __name__ == "__main__":
    POP = TenorPoP()
    IDS = TenorPoP().get_pop_ids()
    POPI = TenorPoP(1)
    print POPI.get_flavor_details()

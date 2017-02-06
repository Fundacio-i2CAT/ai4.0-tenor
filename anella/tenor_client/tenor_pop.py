#!/usr/bin/python
# -*- coding: utf-8 -*-
"""TeNOR PoP Class"""
"""Uses tenor ns-manager/routes/dc.rb """

import requests
import json
import ConfigParser


CONFIG = ConfigParser.RawConfigParser()
CONFIG.read('config.cfg')

DEFAULT_TENOR_URL = format('{0}:{1}'.format(
    CONFIG.get('tenor', 'url'),
    CONFIG.get('tenor', 'port')))

DEFAULT_VNFP_URL = format('{0}:{1}'.format(
    CONFIG.get('tenor', 'url'),
    CONFIG.get('tenor', 'vnfp_port')))

class TenorPoP(object):
    """Represents a TeNOR PoP"""

    def __init__(self, pop_id=None, tenor_url=DEFAULT_TENOR_URL,
                 vnfp_url=DEFAULT_VNFP_URL):
        self._tenor_url = tenor_url
        self._vnfp_url = vnfp_url
        self._pop_id = int(pop_id)
        self._name = None
        self._orch = None

    def retrieve(self):
        """Gets the PoP Name"""
        url = '{0}/pops/dc/{1}'.format(DEFAULT_TENOR_URL, self._pop_id)
        try:
            resp = requests.get(url)
        except:
            raise IOError('{0} instance unreachable'.format(DEFAULT_TENOR_URL))
        try:
            json.loads(resp.text)
        except:
            raise ValueError('Decoding PoP response json response failed')
        pop = json.loads(resp.text)
        self._name = pop['name']
        self._orch = pop['orch']
        return pop

    def get_server_details(self):
        """Gets the server details"""
        url = '{0}/pops/servers/{1}'.format(DEFAULT_TENOR_URL, self._pop_id)
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
        """Gets the quotas on the PoP"""
        url = '{0}/pops/quotas/{1}'.format(DEFAULT_TENOR_URL, self._pop_id)
        try:
            resp = requests.get(url)
        except:
            raise IOError('{0} PoP unreachable'.format(self._pop_id))
        try:
            quotas = json.loads(resp.text)
        except:
            raise ValueError('Decoding PoP response json response failed')
        return quotas['quota_set']

    def get_network_quota_details(self):
        """Gets the quotas on the PoP"""
        url = '{0}/pops/network_quotas/{1}'.format(DEFAULT_TENOR_URL, self._pop_id)
        try:
            resp = requests.get(url)
        except:
            raise IOError('{0} PoP unreachable'.format(self._pop_id))
        try:
            quotas = json.loads(resp.text)
        except:
            raise ValueError('Decoding PoP response json response failed')
        return quotas['quota']

    def get_limits(self):
        '''Get limits and quotas'''
        url = '{0}/pops/limits/{1}'.format(DEFAULT_TENOR_URL, self._pop_id)
        try:
            resp = requests.get(url)
        except:
            raise IOError('{0} PoP unreachable'.format(self._pop_id))
        try:
            limits = json.loads(resp.text)
        except:
            raise ValueError('Decoding PoP response json response failed')
        return limits['limits']

    def get_network_details(self):
        """Gets networks information"""
        url = '{0}/pops/networks/{1}'.format(DEFAULT_TENOR_URL, self._pop_id)
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
        """Gets used floating_ips"""
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

    def get_keypair_details(self):
        """Get used keypairs"""
        url = '{0}/pops/keypairs/{1}'.format(DEFAULT_TENOR_URL, self._pop_id)
        try:
            resp = requests.get(url)
        except:
            raise IOError('{0} PoP unreachable'.format(self._pop_id))
        try:
            keypairs = json.loads(resp.text)
        except:
            raise ValueError('Decoding PoP response json response failed')
	keypairs_used = len(keypairs['keypairs'])
	keypairs_max = self.get_limits()['absolute']['maxTotalKeypairs']
        return {'keypairs_quota': keypairs_max, 'keypairs_used': keypairs_used, 'keypairs_ratio': float(keypairs_used)/float(keypairs_max)}

    def get_secutity_groups_details(self):
        '''gets used and active security groups'''
        sec_groups_max = self.get_limits()['absolute']['maxSecurityGroups']
        sec_groups_used = self.get_limits()['absolute']['totalSecurityGroupsUsed']
	return {'security_groups_quota': sec_groups_max, 'security_groups_used': sec_groups_used, 'security_groups_ratio': float(sec_groups_used)/float(sec_groups_max)}
        
    def get_instance_details(self):
	'''get number of used and quota of images'''
        instances_max = self.get_limits()['absolute']['maxTotalInstances']
        instances_used = self.get_limits()['absolute']['totalInstancesUsed']
        return {'instances_quota': instances_max, 'instances_used': instances_used, 'instances_ratio': float(instances_used)/float(instances_max)}

    def get_routers_details(self):
	'''get used and active router'''
        url = '{0}/pops/routers/{1}'.format(DEFAULT_TENOR_URL, self._pop_id)
        try:
            resp = requests.get(url)
        except:
            raise IOError('{0} PoP unreachable'.format(self._pop_id))
        try:
            routers = json.loads(resp.text)
        except:
            raise ValueError('Decoding PoP response json response failed')
	routers_max = self.get_network_quota_details()['router']
	routers_used = routers
        return {'routers_quota': routers_max, 'routers_used': routers_used, 'routers_ratio': float(routers_used)/float(routers_max)}
 

    def get_core_details(self):
        """Gets used and active cores"""
        servers = self.get_server_details()
        quota = self.get_quota_details()
        cores = int(quota['cores'])
        used_cores = 0
        for server in servers:
            if server['status'].upper() == 'ACTIVE':
                used_cores = used_cores+int(server['flavor']['detail']['vcpus'])
        return {'quota': cores, 'used': used_cores, 'ratio': float(used_cores)/float(cores)}

    def get_ram_details(self):
        """Gets used ram active"""
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
        """Gets flavor details"""
        url = '{0}/pops/flavours/{1}'.format(DEFAULT_TENOR_URL, self._pop_id)
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

    def get_cachedimgs(self, vm_image):
        self.retrieve()
        body = {'vm_image': vm_image, 'vim_url': self._orch}
        url = '{0}/vnf-provisioning/cachedimg'.format(self._vnfp_url)
        resp = requests.post(url,
                             headers={'Content-Type': 'application/json'},
                             json=body)
        if resp.status_code == 404:
            return []
        try:
            rits = json.loads(resp.text)
        except:
            raise ValueError('Decoding PoP response json response failed')
        for rit in rits:
            rit['pop_id'] = self._pop_id
        return rits

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

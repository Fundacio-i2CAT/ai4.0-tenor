#!/usr/bin/python
# -*- coding: utf-8 -*-
"""TeNOR Network Service Instance Class and Client"""

import requests
import json
import uuid
from tenor_vnfi import TenorVNFI
from template_management import create_ssh_client
from template_management import render_template
from models.instance_configuration import InstanceConfiguration
from models.tenor_messages import CriticalError
from models.tenor_messages import InstanceDenial
from urlparse import urlparse

from scp import SCPClient
from Crypto.PublicKey import RSA
import os
import ConfigParser

CONFIG = ConfigParser.RawConfigParser()
CONFIG.read('config.cfg')

DEFAULT_TENOR_URL = format('{0}:{1}'.format(
    CONFIG.get('tenor', 'url'),
    CONFIG.get('tenor', 'port')))

def runtime_mapping(name, tenor_nsi):
    addresses = tenor_nsi.get_addresses()
    for addr in addresses:
        if (name.upper() == 'FLOATING_IP') and (addr['OS-EXT-IPS:type'].upper() == 'FLOATING'):
            return addr['addr']
        if (name.upper() == 'FIXED_IP') and (addr['OS-EXT-IPS:type'].upper() == 'FIXED'):
            return addr['addr']
    return None

class TenorNSI(object):
    """Represents a TeNOR NS Instance"""

    def __init__(self, nsi_id, tenor_url=DEFAULT_TENOR_URL):
        self._nsi_id = nsi_id
        self._tenor_url = tenor_url
        self._state = "UNKNOWN"
        self._addresses = []
        self._image_id = None
        self._image_url = None
        self._code = None
        self.retrieve()

    def __repr__(self):
        return "{0} {1} {2}".format(self._nsi_id, self._state, self._addresses)

    def retrieve(self):
        """Get NSI information from tenor instance"""
        try:
            resp = requests.get('{0}/ns-instances/{1}'.format(
                self._tenor_url, self._nsi_id))
        except IOError:
            raise IOError('{0} instance unreachable'.format(self._tenor_url))
        try:
            nsi = json.loads(resp.text)
        except:
            self._state = 'UNKNOWN'
            return {}
        if 'vnfrs' in nsi:
            if len(nsi['vnfrs']) > 0:
                vnfr = nsi['vnfrs'][0]
                if 'vnfr_id' in vnfr:
                    vnfi = TenorVNFI(vnfr['vnfr_id'])
                    self._image_id = vnfi.get_image_id()
                    self._image_url = vnfi.get_image_url()
                if 'server' in vnfr:
                    if 'status' in vnfr['server']:
                        if vnfr['server']['status'].upper() == 'ACTIVE':
                            self._state = 'RUNNING'
                        if vnfr['server']['status'].upper() == 'SHUTOFF':
                            self._state = 'DEPLOYED'
                    if 'addresses' in vnfr['server']:
                        self._addresses = vnfr['server']['addresses']
        return nsi

    def create_provider_key(self):
        """Creates a new RSA key pair and updates the machine with the public one"""
        for addr in self._addresses[0][1]:
            if addr['OS-EXT-IPS:type'].upper() == 'FLOATING':
                server_ip = addr['addr']
        key = RSA.generate(2048)
        pubkey = key.publickey()
        icds = InstanceConfiguration.objects(service_instance_id=self._nsi_id)

        if len(icds) < 1:
            print "ICD NOT FOUND"
            return
        ssh = create_ssh_client(server_ip, 'root', icds[0].pkey)
        command = 'echo \'{0}\' >> /root/.ssh/authorized_keys'.format(pubkey.exportKey('OpenSSH'))
        print command
        stdin, stdout, stderr = ssh.exec_command(command)
        print stdout.readlines()
        print stderr.readlines()
        ssh.close()
        # returns the private key
        return key.exportKey('PEM')

    def get_addresses(self):
        return self._addresses[0][1]

    def configure(self):
        """Configures the instance according to consumer needs"""
        for addr in self._addresses[0][1]:
            if addr['OS-EXT-IPS:type'].upper() == 'FLOATING':
                server_ip = addr['addr']
        icds = InstanceConfiguration.objects(service_instance_id=self._nsi_id)

        if len(icds) < 1:
            print "ICD NOT FOUND"
            return
        try:
            ssh = create_ssh_client(server_ip, 'root', icds[0].pkey)
        except:
            crite = CriticalError(service_instance_id=self._nsi_id,
                                  message='Failed to connect to {0}'.format(server_ip),
                                  code='CONFIGURATION_FAILED')
            crite.save()
            return
        scp = SCPClient(ssh.get_transport())

        for cpar in icds[0].consumer_params:
            filename = cpar.path
            if 'content' in cpar:
                content = cpar.content.encode('utf-8')
                command = 'echo \'{0}\' > {1}'.format(content,
                                                      filename)
                print command
                try:
                    stdin, stdout, stderr = ssh.exec_command(command)
                except:
                    crite = CriticalError(service_instance_id=self._nsi_id,
                                          message='Failed to configure {0} configuration file'.format(filename),
                                          code='CONFIGURATION_FAILED')
                    crite.save()
                    return
                print stdout.readlines()
                print stderr.readlines()
            if 'fields' in cpar:
                print 'Getting {0}'.format(filename)
                template_id = str(uuid.uuid4())
                template_filename = '/tmp/{0}'.format(template_id)
                try:
                    scp.get(filename, template_filename)
                except:
                    crite = CriticalError(service_instance_id=self._nsi_id,
                                          message='Failed to retrieve {0} configuration file'.format(filename),
                                          code='CONFIGURATION_FAILED')
                    crite.save()
                    return
                keyvalues = {}
                for item in cpar.fields:
                    if item.runtime:
                        runtime_value = runtime_mapping(item.name, self)
                        if runtime_value:
                            print "RUNTIME"
                            print item.name
                            print runtime_value
                            keyvalues[item.name] = runtime_value
                    else:
                        keyvalues[item.name] = item.value
                result = render_template(template_id, keyvalues)
                render_filename = '/tmp/{0}'.format(uuid.uuid4())
                with open(render_filename, 'w') as fhandle:
                    fhandle.write(result)
                print 'Sending {0}'.format(filename)
                try:
                    scp.put(render_filename, filename)
                except:
                    crite = CriticalError(service_instance_id=self._nsi_id,
                                          message='Failed to write {0} configuration file'.format(filename),
                                          code='CONFIGURATION_FAILED')
                    crite.save()
                    return
                print 'Removing temporary files'
                os.remove(template_filename)
                os.remove(render_filename)

        print 'Closing ssh client'
        ssh.close()

    def start(self):
        """Sets active all the VNF instances associated"""
        try:
            resp = requests.put('{0}/ns-instances/{1}/start'.format(
                self._tenor_url, self._nsi_id))
            self.retrieve()
        except:
            raise IOError('Error starting {0}'.format(self._nsi_id))
        return resp

    def stop(self, denied=False):
        """Sets shutoff all the VNF instances associated"""
        try:
            resp = requests.put('{0}/ns-instances/{1}/stop'.format(
                self._tenor_url, self._nsi_id))
            self.retrieve()
            if denied==True:
                insden = InstanceDenial(service_instance_id=self._nsi_id, message='DENIED')
                insden.save()
                resp = type('', (object,), {'text': json.dumps({'message': 'Successfully sent deny state signal',
                                                                'state': 'DENIEDX'}),'status_code': 200})()
        except:
            raise IOError('Error stoping {0}'.format(self._nsi_id))
        return resp

    def delete(self):
        """Deletes the NSI"""
        try:
            resp = requests.delete('{0}/ns-instances/{1}'.format(
                self._tenor_url, self._nsi_id))
        except IOError:
            raise IOError('Error deleting {0}'.format(self._nsi_id))
        return resp

    def create_image(self, name_image):
        try:
            resp = requests.post('{0}/ns-instances/{1}/snapshot'.format(self._tenor_url, self._nsi_id),
                                 headers={'Content-Type': 'application/json'},
                                 json={'name_image': name_image})
        except:
            raise IOError('Error creating snapshot from {0}'.format(self._nsi_id))
        return

    def get_state_and_addresses(self):
        """Returns state and addresses associated with the NSI"""
        addresses = []
        self.retrieve()
        runtime_params = []
        for adr in self._addresses:
            for ipif in adr[1]:
                if ipif['OS-EXT-IPS:type'] == 'floating':
                    runtime_params.append({'name': 'floating_ip',
                                           'desc': 'Service instance IP address',
                                           'value': ipif['addr']})
                addresses.append({'OS-EXT-IPS:type': ipif['OS-EXT-IPS:type'],
                                  'addr': ipif['addr']})

        failed = False
        crites = CriticalError.objects(service_instance_id=self._nsi_id)
        if len(crites) > 0:
            failed = True

        if failed:
            self._state = 'FAILED'
            self._code = crites[0].code

        denied = False
        insdens = InstanceDenial.objects(service_instance_id=self._nsi_id)
        if len(insdens) > 0:
            denied = True

        if denied:
            self._state = 'DENIED'

        result = {'service_instance_id': self._nsi_id,
                  'state': self._state,
                  'addresses': addresses,
                  'runtime_params': runtime_params}
        if self._code:
            result['code'] = self._code
        if self._image_id:
            result['created_image'] = {'vm_image': self._image_id,
                                       'vm_image_format': 'openstack_id'}
        if self._image_url:
            image_path = None
            try:
                parsed_url = urlparse(self._image_url)
                image_path = parsed_url.path.split('/')[-1]
            except:
                image_path = None
            if image_path:
                result['image_path'] = image_path
        return result

    @staticmethod
    def get_nsi_ids():
        """Returns the list of NSI registered in TeNOR"""
        try:
            resp = requests.get('{0}/ns-instances/ids'.format(DEFAULT_TENOR_URL))
        except:
            raise IOError('{0} instance unreachable'.format(DEFAULT_TENOR_URL))
        try:
            json.loads(resp.text)
        except:
            raise ValueError('Decoding NSI response json response failed')
        ids = []
        for nsi in json.loads(resp.text):
            ids.append(nsi['id'])
        return ids

if __name__ == "__main__":
    NSS = TenorNSI.get_nsi_ids()
    CONFIG = {'config': [
        {
            "target_filename": "/var/www/html/index.html",
            "context": {
                "name": "MONDAY",
                "picture": "https://cdn3.iconfinder.com/data/icons/users-6/100/2-512.png",
                "cv": "laksdj laskjd aslkjd "
            }
        },
        {
            "target_filename": "/root/customer_ip.txt",
            "content": "192.168.1.1"
        }
    ]
           }
    for n in NSS:
        NS = TenorNSI(n)
        print n
        print NS.get_state_and_addresses()
        NS.configure('172.24.4.207', CONFIG)

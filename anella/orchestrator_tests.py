#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Anella 4.0 Orchestrator Tests"""

from start import PORT, URL_PREFIX
import json
import unittest
import requests
import random
import time
import ConfigParser
import paramiko

CONFIG = ConfigParser.RawConfigParser()
CONFIG.read('config.cfg')
POP_ID = int(CONFIG.get('tenor', 'i2cat_pop'))

BASE_URL = 'http://localhost:{0}{1}'.format(PORT, URL_PREFIX)

OVNFD_EXAMPLE = {
    "name": "TEST",
    "vdu":
    {
        "vm_image": "6d2b10db-1716-4541-9514-542e91594d2a",
        "vm_image_format": "OpenstacK_id",
        "shell": "#!/bin/bash\\necho 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCTyrMs/iliz2PPAGACyGWwC7OqoIDgoStpiiXcJIAElaLiiAhlOdhCJP6okE2WzkuMf4XD80fVm/yikrjSRTVwph981KEEcAH+mRWThkoItaPqDLPh79AJfT1Ud48FQbG8MZu91X+E4ecnYQH/1bPRxiumWQLNrHmIhY8aIKv/xPCF8zZBYjG6BK/g2L22h4Ky6VI07uyzHyIk78OxUZTpQcb+jnFpJlVOZreRLc8RE6pDF17h4ZhrEmv0tvdWiubk46cbEUwOvGq9wWxFKReEQubC+7/2WNcQnkAylDxzbR9pF/RlomuwcBWSycQ8RVpmr8T1cydaBpi9cbBB2DOn alfonso@knightmare' >> /root/.ssh/authorized_keys",
        "storage_amount": 6,
        "flavor": "m1.medium",
        "vcpus": 1
    }
}

CATALOG_EXAMPLE = {
    "context" : {
        "runtime_params" : [
            {
		"name" : "wwwwww",
		"desc" : "sssssss"
            }
	],
	"name_image" : "TEST",
	"tenor_url" : "http://localhost:4000",
        "vm_image": "6d2b10db-1716-4541-9514-542e91594d2a",
        "vm_image_format": "openstack_id",
	"flavor" : "m1.medium",
	"consumer_params" : [
            {
		"path" : "/var/www/html/index.html",
		"fields" : [
                    {
			"required": True,
			"name" : "floating_ip",
			"desc" : "Instance's floating IP",
			"value" : "floating_ip",
			"runtime" : True
		    },
                    {
			"required" : True,
			"name" : "name",
			"desc" : "Name of the consumer",
			"value" : "yo vot&eacute; a kodos"
                    },
                    {
			"required" : True,
			"name" : "picture",
			"desc" : "Foto del consumer",
			"value" : "https://upload.wikimedia.org/wikipedia/en/d/d4/Mickey_Mouse.png"
                    },
                    {
			"required" : True,
			"name" : "cv",
			"desc" : "CV del consumer",
			"value" : "wiLL cOdE HtML for FOOD"
                    }
		]
            },
            {
		"path" : "/root/chequeo.txt",
		"content" : "YO ESTUVE AQUI CON MONGOENGINE!!!!!!!!!!!!!!!!!!!!!!!!!"
	    }
	]
    }
}

ADAM_EXAMPLE = {
    "context" : {
	"runtime_params" : [
            {
		"name" : "wwwwww",
		"desc" : "sssssss"
            }
	],
	"name_image" : "TEST",
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
			"required": True,
			"name" : "floating_ip",
			"desc" : "Instance's floating IP",
			"value" : "floating_ip",
			"runtime" : True
		    },
                    {
			"required": True,
			"name" : "fixed_ip",
			"desc" : "Instance's fixed IP",
			"value" : "fixed_ip",
			"runtime" : True
		    },
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

class OrchestratorTestCase(unittest.TestCase):
    """Full test"""

    def setUp(self):
        """Initial setup"""
        self._vnfs = []
        self._nss = []
        self._nsis = []

    def test_01(self):
        """PoP tests"""
        resp = requests.get('{0}/pop'.format(BASE_URL))
        assert resp.status_code == 200
        pops = json.loads(resp.text)
        for tpop in pops:
            if tpop['pop_id'] == 1:
                continue
            presp = requests.get('{0}/pop/{1}'.format(BASE_URL, tpop['pop_id']))
            assert presp.status_code == 200
            pdata = json.loads(presp.text)
            assert 'pop_id' in pdata
            assert 'orch' in pdata
            assert 'name' in pdata
            print "- CHECKING {0}".format(pdata['name'])
            print "\t * HEAT URL: ", pdata['orch']
            resources = ['flavors', 'quotas', 'servers', 'ram',
                         'cores', 'floating_ips', 'networks']
            for res in resources:
                url = '{0}/pop/{1}/{2}'.format(BASE_URL, tpop['pop_id'],res)
                print "\t -- {0}".format(res.upper())
                rresp = requests.get(url)
                assert rresp.status_code == 200
                rrdata = json.loads(rresp.text)
                sample = rresp.text[:100] + (rresp.text[100:] and '...')
                print "\t\t $-$ ", sample.strip()
            print

    def test_02(self):
        """Gets NS instances"""
        resp = requests.get('{0}/service/instance'.format(BASE_URL))
        assert resp.status_code == 200
        instances = json.loads(resp.text)
        if len(instances) > 0:
            assert 'service_instance_id' in instances[0]
            for ins in instances:
                assert ins['state'].upper() in ('RUNNING', 'DEPLOYED', 'UNKNOWN', 'FAILED')
                iresp = requests.get('{0}/service/instance/{1}'.format(BASE_URL, ins['service_instance_id']))
                idata = json.loads(iresp.text)
                assert 'service_instance_id' in idata
                hresp = requests.get('{0}/service/instance/{1}/history'.format(BASE_URL, ins['service_instance_id']))
                hdata = json.loads(hresp.text)
                assert hresp.status_code == 200
        return instances

    def start_stop(self, prv, nxt, expected):
        """Aux. method to set prv state instances to nxt asserting expected status_code"""
        instances = self.test_02()
        f_instances = [x for x in instances if x['state'].upper() == prv]
        for ins in f_instances:
            url = '{0}/service/instance/{1}'.format(BASE_URL,
                                                    ins['service_instance_id'])
            resp = requests.put(url,
                                headers={'Content-Type': 'application/json'},
                                json={'state': nxt})
            assert resp.status_code == expected

    def test_03(self):
        """Testing start/stop"""
        self.start_stop('RUNNING', 'DEPLOYED', 200)
        self.start_stop('DEPLOYED', 'RUNNING', 200)

    def post_vnf(self, preserve=False):
        """Posts a new VNF"""
        url = '{0}/vnf'.format(BASE_URL)
        resp = requests.post(url, headers={'Content-Type': 'application/json'},
                             json=OVNFD_EXAMPLE)
        assert resp.status_code == 200
        vnf_data = json.loads(resp.text)
        assert 'vnf_id' in vnf_data
        if not preserve:
            self._vnfs.append(vnf_data['vnf_id'])

    def post_ns(self, preserve=False):
        """Posts a new NS"""
        vresp = requests.get('{0}/vnf'.format(BASE_URL))
        assert vresp.status_code == 200
        url = '{0}/ns'.format(BASE_URL)
        resp = requests.post(url, headers={'Content-Type': 'application/json'},
                             json={'vnf_id': random.choice(self._vnfs),
                                   'name': 'randomTest'})
        assert resp.status_code == 200
        data = json.loads(resp.text)
        assert 'ns_id' in data
        if not preserve:
            self._nss.append(data['ns_id'])

    def test_04(self):
        """Posts VNFs"""
        self.post_vnf()
        self.post_vnf()

    def test_05(self):
        """Posts NSs"""
        self.post_vnf()
        self.post_vnf()
        self.post_vnf()
        self.post_vnf()
        self.post_ns()
        self.post_ns()
        self.post_ns()
        self.post_ns()
        self.post_ns()
        self.post_ns()

    def instantiate_ns(self, preserve=False):
        """Instantates a NS, injects a random number
        in apache index.html and waits to stack deployment to check"""
        requests.get('{0}/ns'.format(BASE_URL))
        requests.get('{0}/pop'.format(BASE_URL))
        pop_id = POP_ID
        tns = random.choice(self._nss)
        ns_id = tns
        random_number = random.randint(0, 10000)
        body = {'pop_id': pop_id,
                'callback_url': 'http://localhost:80',
                'context': {
                    'consumer_params': [
                        {
                            'path': '/var/www/html/index.html',
                            'content': '{0}'.format(random_number)
                        }
                    ]}
            }

        url = '{0}/ns/{1}'.format(BASE_URL, ns_id)
        resp = requests.post(url,
                             headers={'Content-Type': 'application/json'},
                             json=body)
        assert resp.status_code == 200
        data = json.loads(resp.text)
        assert 'service_instance_id' in data
        nsid = data['service_instance_id']
        assert data['state'].upper() == 'PROVISIONED'
        url = '{0}/service/instance/{1}'.format(BASE_URL, nsid)
        while True:
            time.sleep(60)
            resp = requests.get(url)
            assert resp.status_code == 200
            nsi = json.loads(resp.text)
            if nsi['state'].upper() == 'RUNNING' or nsi['state'].upper() == 'FAILED':
                break
        resp = requests.get(url)
        ipaddr = None
        nsi = json.loads(resp.text)
        for addr in nsi['addresses']:
            if addr['OS-EXT-IPS:type'] == 'floating':
                ipaddr = addr['addr']
        # checks also the key generation feature
        key_url = '{0}/service/instance/{1}/key'.format(BASE_URL, nsid)
        key_resp = requests.get(key_url)
        with open('keys/test_key.pem', 'w') as key_file:
            key_file.write(key_resp.text)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ipaddr, username='root',
                    key_filename='keys/test_key.pem',
                    timeout=15)
        command = 'ls -laht /'
        stdin, stdout, stderr = ssh.exec_command(command)
        assert len(stdout.readlines()) > 1
        assert len(stderr.readlines()) == 0
        ssh.close()
        webresp = requests.get('http://{0}'.format(ipaddr))
        assert random_number == int(webresp.text)
        if not preserve:
            self._nsis.append(nsid)

    def atest_06(self):
        """Posts vnf, ns and instantiates it"""
        self.post_vnf(False)
        self.post_ns(False)
        self.instantiate_ns()

    def atest_07(self):
        """Posts service/instance one round mode"""
        url = '{0}/service/instance'.format(BASE_URL)
        resp = requests.post(url, headers={'Content-Type': 'application/json'},
                             json=CATALOG_EXAMPLE)
        assert resp.status_code == 200

    def test_08(self):
        """Posts service/instance one round mode at Adam with fixed network/pop"""
        url = '{0}/service/instance'.format(BASE_URL)
        resp = requests.post(url, headers={'Content-Type': 'application/json'},
                             json=ADAM_EXAMPLE)
        assert resp.status_code == 200

    def tearDown(self):
        """tearDown"""
        while len(self._nsis) > 0:
            nsi = self._nsis.pop()
            url = '{0}/service/instance/{1}'.format(BASE_URL, nsi)
            resp = requests.delete(url)
            assert resp.status_code == 200

        while len(self._nss) > 0:
            vnf = self._nss.pop()
            url = '{0}/ns/{1}'.format(BASE_URL, vnf)
            resp = requests.delete(url)
            assert resp.status_code == 200

        while len(self._vnfs) > 0:
            vnf = self._vnfs.pop()
            url = '{0}/vnf/{1}'.format(BASE_URL, vnf)
            resp = requests.delete(url)
            assert resp.status_code == 200

if __name__ == '__main__':
    unittest.main()

#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import json

KEYSTONE_URL = 'http://dev.anella.i2cat.net:5000/v3'
USER = 'admin'
PASSWORD = 'i2cat'
AUTH_TEMPLATE = {'auth':
                 {'scope':
                  {'project':
                   {'domain': {'id': 'default'},
                    'name': 'admin'}},
                  'identity':
                  {'password':
                   {'user':
                    {'domain':
                     {'id': 'default'},
                     'password': PASSWORD, 'name': USER}}, 'methods':
                   ['password']}}}


def get_token():
    resp = requests.post('{0}/auth/tokens'.format(KEYSTONE_URL),
                  headers={'Content-Type': 'application/json'},
                  json=AUTH_TEMPLATE)
    if resp.status_code == 201:
        return resp.headers['X-Subject-Token']
    else:
        return resp.status_code

def get_user_list(token):
    resp = requests.get('{0}/users'.format(KEYSTONE_URL),
                       headers={'Content-Type': 'application/json','X-Auth-Token': token})
    return resp.text

def get_role_list(token):
    resp = requests.get('{0}/roles'.format(KEYSTONE_URL),
                       headers={'Content-Type': 'application/json','X-Auth-Token': token})
    return resp.text

def post_roles(token):
    resp = requests.post('{0}/roles'.format(KEYSTONE_URL),
                         headers={'Content-Type': 'application/json','X-Auth-Token': token},
                         json={'role': {'name': 'User.Provider'}})
    resp = requests.post('{0}/roles'.format(KEYSTONE_URL),
                         headers={'Content-Type': 'application/json','X-Auth-Token': token},
                         json={'role': {'name': 'User.Client'}})
    return resp.text

if __name__ == '__main__':
    token = get_token()
    print token
    print get_role_list(token)

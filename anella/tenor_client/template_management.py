#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Template management and scp routine"""

from jinja2 import Environment, FileSystemLoader
import paramiko
import StringIO

def create_ssh_client(server, user, pkey, timeout=15):
    """Returns the ssh client"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    nraf = StringIO.StringIO(pkey)
    private_key = paramiko.RSAKey.from_private_key(nraf)
    nraf.close()
    client.connect(server, username=user,
                    pkey=private_key,
                    timeout=timeout)
    return client

def render_template(templ_fn, context):
    """Process the template"""
    path = '/tmp/'
    templ_env = Environment(
        autoescape=False,
        loader=FileSystemLoader(path),
    trim_blocks=False)
    return templ_env.get_template(templ_fn).render(context).encode('utf8')

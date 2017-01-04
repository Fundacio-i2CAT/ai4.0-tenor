#!/usr/bin/python
# -*- coding: utf-8 -*-
"""PoP API"""

from tenor_client.tenor_pop import TenorPoP
import flask_restful
from flask_restful import abort

class PoP(flask_restful.Resource):
    """PoP related resources"""
    def __init__(self):
        pass

    def get(self, pop_id=None, resource=None):
        ids = TenorPoP.get_pop_ids()
        result = []
        if pop_id:
            for pid in ids:
                if pid == int(pop_id):
                    tpop = TenorPoP(pid)
                    if not resource:
                        pop_info = tpop.retrieve()
                        return {'pop_id': pop_id, 'name': pop_info['name'],
                                'orch': pop_info['orch']}
                    if resource == 'flavors':
                        return {'flavors': tpop.get_flavor_details()}
                    if resource == 'quotas':
                        return {'quotas': tpop.get_quota_details()}
                    if resource == 'servers':
                        return {'servers': tpop.get_server_details()}
                    if resource == 'ram':
                        return {'ram': tpop.get_ram_details()}
                    if resource == 'cores':
                        return {'cores': tpop.get_core_details()}
                    if resource == 'floating_ips':
                        return {'floating_ips': tpop.get_floating_ip_details()}
                    elif resource == 'networks':
                        return {'networks': tpop.get_network_details()}
            if resource:
                abort(404,
                      message='{0} PoP nf or rsrc {1} not in (networks,flavors)'.format(pop_id, resource))
        for pop_sid in ids:
            my_pop = TenorPoP(pop_sid)
            pop_info = my_pop.retrieve()
            result.append({'pop_id': int(pop_sid),
                           'name': pop_info['name'],
                           'orch': pop_info['orch']})
        return result

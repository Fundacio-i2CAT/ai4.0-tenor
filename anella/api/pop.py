#!/usr/bin/python
# -*- coding: utf-8 -*-
"""PoP API"""

from tenor_client.tenor_pop import TenorPoP
import flask_restful
from flask import request
from flask_restful import abort

class IsCached(flask_restful.Resource):
    """Endpoint to query cached images in VIMs"""
    def __init__(self):
        pass

    def post(self, pop_id=None):
        """Requests TeNOR to ask the VIM(s) if an image from an URL is cached"""
        data = request.get_json()
        vm_image = data['vm_image']
        if pop_id:
            tpop = TenorPoP(pop_id)
            cachedimgs = tpop.get_cachedimgs(vm_image)
            if len(cachedimgs) > 0:
                return cachedimgs[0]
            else:
                abort(404,
                      message='Image at {0} not cached at PoP {1}'.format(vm_image, pop_id))
        ids = TenorPoP.get_pop_ids()
        total = []
        for pid in ids:
            tpop = TenorPoP(pid)
            cachedimgs = tpop.get_cachedimgs(vm_image)
            if len(cachedimgs) > 0:
                total.append(cachedimgs[0])
        if len(total) > 0:
            return total
        else:
                abort(404,
                      message='Image at {0} is not cached anywhere'.format(vm_image))

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

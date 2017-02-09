# -*- coding: utf-8 -*-
#
# TeNOR - NS Manager
#
# Copyright 2014-2016 i2CAT Foundation, Portugal Telecom Inovação
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# @see DcController
class DcController < TnovaManager

    # port is 4000. Need to add exact path for the calls
    # @method get_pops_dc
    # @overload get '/pops/dc/:id'
    #  Returns a DCs
    get '/dc' do
        begin
            return 200, Dc.all.to_json
        rescue => e
            logger.error e
            logger.error 'Error Establishing a Database Connection'
            return 500, 'Error Establishing a Database Connection'
        end
    end

    # @method post stack
    # @overload post "/stack"
    # post stack URL to query if it exists on the VIM (ANELLA)
    post '/stack' do
        begin
            return 415 unless request.content_type == 'application/json'
            stack_info, errors = parse_json(request.body.read)
            dc = nil
            begin
                dcs = Dc.find()
                Dc.each do |idc|
                    popUrls = getPopUrls(idc)
                    if popUrls[:orch] == stack_info['vim_url']
                        dc = idc
                        break
                    end
                end
                if dc.nil?
                    halt 404, "DC not found"
                end
            rescue Mongoid::Errors::DocumentNotFound => e
                logger.error 'DC not found'
                return 404
            end
            popUrls = getPopUrls(dc)

            admin_credentials, errors = authenticate_anella(popUrls[:keystone], dc["tenant_name"], dc['user'], dc['password'])
            tenant_id = admin_credentials[:tenant_id]
            auth_token = admin_credentials[:token]
            begin
                response = RestClient.get stack_info['stack_url'], 'X-Auth-Token' => auth_token, :accept => :json
                stack = JSON.parse(response.body)
                if stack['stack']['stack_status'].casecmp('create_complete').zero?
                    response
                else
                    halt 404
                end
            rescue Errno::ECONNREFUSED
                logger.error "VIM unreachable"
                halt 500, 'VIM unreachable'
            rescue RestClient::ResourceNotFound
                logger.error 'Already removed from the VIM.'
                halt 404
            rescue RestClient::Unauthorized
                logger.error 'Unauthorized'
                halt 401
            rescue => e
                logger.error e
                halt 500
            end
        end
    end

    # @method get dc_servers
    # @overload get "/servers/:id"
    # Get the servers running for the vim (ANELLA)
    get '/servers/:id' do |id|
        begin
            begin
                dc = Dc.find(id.to_i)
            rescue Mongoid::Errors::DocumentNotFound => e
                logger.error 'DC not found'
                return 404
            end
            popUrls = getPopUrls(dc)
            compute_url = popUrls[:compute]
            admin_credentials, errors = authenticate_anella(popUrls[:keystone], dc["tenant_name"], dc['user'], dc['password'])
            tenant_id = admin_credentials[:tenant_id]
            auth_token = admin_credentials[:token]
            begin
                response = RestClient.get compute_url +"/#{tenant_id}/servers/detail", 'X-Auth-Token' => auth_token, :accept => :json
            rescue Errno::ECONNREFUSED
                # halt 500, 'VIM unreachable'
                logger.error "VIM unreachable"
            rescue RestClient::ResourceNotFound
                logger.error 'Already removed from the VIM.'
                return 404
            rescue => e
                logger.error e
                #logger.error e.response
                return
                # halt e.response.code, e.response.body
            end
            servers = JSON.parse(response.body)
            servers['servers'].each do |server|
                if server['flavor']['links'].kind_of? Array
                    begin
                        flavor_uri = URI(server['flavor']['links'][0]['href'])
                        flavor = RestClient.get compute_url+flavor_uri.path, 'X-Auth-Token' => auth_token, :accept => :json
                        server['flavor']['detail'] = JSON.parse(flavor.body)['flavor']
                    rescue => e
                        logger.info e
                    end
                end
            end
            servers.to_json()
        end
    end

    # @method get dc_quotas
    # @overload get "/pops/quotas/:id"
    # Get the quotas avaliable for the vim (ANELLA)
    get '/quotas/:id' do |id|
        begin
            begin
                dc = Dc.find(id.to_i)
            rescue Mongoid::Errors::DocumentNotFound => e
                logger.error 'DC not found'
                return 404
            end
            popUrls = getPopUrls(dc)
            compute_url = popUrls[:compute]
            admin_credentials, errors = authenticate_anella(popUrls[:keystone], dc["tenant_name"], dc['user'], dc['password'])
            tenant_id = admin_credentials[:tenant_id]
            auth_token = admin_credentials[:token]
            begin
                # After checking this https://bugs.launchpad.net/openstack-api-site/+bug/1264043
                #      should be: GET {tenant_id}/os-quota-sets/{tenant_id_to_query}
                response = RestClient.get compute_url +"/#{tenant_id}/os-quota-sets/#{tenant_id}", 'X-Auth-Token' => auth_token, :accept => :json
            rescue Errno::ECONNREFUSED
                # halt 500, 'VIM unreachable'
                logger.error "VIM unreachable"
            rescue RestClient::ResourceNotFound
                logger.error 'Already removed from the VIM.'
                return 404
            rescue => e
                logger.error e
                #logger.error e.response
                return
                # halt e.response.code, e.response.body
            end
            response
        end
    end

    # @method get network_quotas
    # @overload get "/pops/network_quotas/:id"
    # Get the network quotas avaliable for the vim (ANELLA)
    get '/network_quotas/:id' do |id|
        begin
            begin
                dc = Dc.find(id.to_i)
            rescue Mongoid::Errors::DocumentNotFound => e
                logger.error 'DC not found'
                return 404
            end
            popUrls = getPopUrls(dc)
            compute_url = popUrls[:compute]
            neutron_url = popUrls[:neutron]
            admin_credentials, errors = authenticate_anella(popUrls[:keystone], dc["tenant_name"], dc['user'], dc['password'])
            tenant_id = admin_credentials[:tenant_id]
            auth_token = admin_credentials[:token]
            begin
                response = RestClient.get neutron_url  +"/quotas/#{tenant_id}", 'X-Auth-Token' => auth_token, :accept => :json
            rescue Errno::ECONNREFUSED
                logger.error "VIM unreachable"
            rescue RestClient::ResourceNotFound
                logger.error 'Already removed from the VIM.'
                return 404
            rescue => e
                logger.error e
                #logger.error e.response
                return
                # halt e.response.code, e.response.body
            end
            response
        end
    end

    # @method get routers
    # @overload get "/pops/routers/:id"
    # Get the routers avaliable for the vim (ANELLA)
    get '/routers/:id' do |id|
        begin
            begin
                dc = Dc.find(id.to_i)
            rescue Mongoid::Errors::DocumentNotFound => e
                logger.error 'DC not found'
                return 404
            end
            popUrls = getPopUrls(dc)
            compute_url = popUrls[:compute]
            neutron_url = popUrls[:neutron]
            admin_credentials, errors = authenticate_anella(popUrls[:keystone], dc["tenant_name"], dc['user'], dc['password'])
            tenant_id = admin_credentials[:tenant_id]
            auth_token = admin_credentials[:token]
            begin
                response = RestClient.get neutron_url  +"/routers", 'X-Auth-Token' => auth_token, :accept => :json
            rescue Errno::ECONNREFUSED
                logger.error "VIM unreachable"
            rescue RestClient::ResourceNotFound
                logger.error 'Already removed from the VIM.'
                return 404
            rescue => e
                logger.error e
                return
            end
            tenant_routers = 0
            json_routers = parse_json(response)
            json_routers[0]["routers"].each do |child|
		if(child["tenant_id"] == tenant_id)
                    print child["tenant_id"]
                    tenant_routers = tenant_routers + 1
		    print "TENANT RO: #{tenant_routers}"
		end
	    end
	    #json_routers[0]["routers"].delete_if do |v|
    	    #	if k == 1?
       	    #	     true
    	    #	else
            #	     v.update
            #	     false
    	    #   end
	    #end

            #for router in json_routers['routers']:
	    #	print router
	    #print json_routers
            return "#{tenant_routers}"
        end
    end

    # @method get dc_limits
    # @overload get "/pops/limits/:id"
    # Get the limits avaliable for the vim (ANELLA)
    get '/limits/:id' do |id|
        begin
            begin
                dc = Dc.find(id.to_i)
            rescue Mongoid::Errors::DocumentNotFound => e
                logger.error 'DC not found'
                return 404
            end
            popUrls = getPopUrls(dc)
            compute_url = popUrls[:compute]
            admin_credentials, errors = authenticate_anella(popUrls[:keystone], dc["tenant_name"], dc['user'], dc['password'])
            tenant_id = admin_credentials[:tenant_id]
            auth_token = admin_credentials[:token]
            begin
                response = RestClient.get compute_url +"/#{tenant_id}/limits", 'X-Auth-Token' => auth_token, :accept => :json
            rescue Errno::ECONNREFUSED
                # halt 500, 'VIM unreachable'
                logger.error "VIM unreachable"
            rescue RestClient::ResourceNotFound
                logger.error 'Already removed from the VIM.'
                return 404
            rescue => e
                logger.error e
                return
            end
            response
        end
    end

    # @method get dc_keypairs
    # @overload get "/pops/keypairs/:id"
    # Get the keypairs of the vim (ANELLA)
    get '/keypairs/:id' do |id|
        begin
            begin
                dc = Dc.find(id.to_i)
            rescue Mongoid::Errors::DocumentNotFound => e
                logger.error 'DC not found'
                return 404
            end
            popUrls = getPopUrls(dc)
            compute_url = popUrls[:compute]
            admin_credentials, errors = authenticate_anella(popUrls[:keystone], dc["tenant_name"], dc['user'], dc['password'])
            tenant_id = admin_credentials[:tenant_id]
            auth_token = admin_credentials[:token]
            begin
                response = RestClient.get compute_url +"/#{tenant_id}/os-keypairs", 'X-Auth-Token' => auth_token, :accept => :json
            rescue Errno::ECONNREFUSED
                # halt 500, 'VIM unreachable'
                logger.error "VIM unreachable"
            rescue RestClient::ResourceNotFound
                logger.error 'Already removed from the VIM.'
                return 404
            rescue => e
                logger.error e
                return
            end
            response
        end
    end


    # @method get dc_networks
    # @overload get "/networks/:id"
    # Get the networks avaliable for the vim (ANELLA)
    get '/networks/:id' do |id|
        begin
            begin
                dc = Dc.find(id.to_i)
            rescue Mongoid::Errors::DocumentNotFound => e
                logger.error 'DC not found'
                return 404
            end
            popUrls = getPopUrls(dc)
            neutron_url = popUrls[:neutron]
            admin_credentials, errors = authenticate_anella(popUrls[:keystone], dc["tenant_name"], dc['user'], dc['password'])
            tenant_id = admin_credentials[:tenant_id]
            auth_token = admin_credentials[:token]
            begin
                response = RestClient.get neutron_url +"/networks", 'X-Auth-Token' => auth_token, :accept => :json
            rescue Errno::ECONNREFUSED
                # halt 500, 'VIM unreachable'
                logger.error "VIM unreachable"
            rescue RestClient::ResourceNotFound
                logger.error 'Already removed from the VIM.'
                return 404
            rescue => e
                logger.error e
                #logger.error e.response
                return
                # halt e.response.code, e.response.body
            end
            response
        end
    end

    # @method get dc_flavours
    # @overload get "/flavours/:id"
    # Get the flavours avaliable for the vim (ANELLA)
    get '/flavours/:id' do |id|
        begin
            begin
                dc = Dc.find(id.to_i)
            rescue Mongoid::Errors::DocumentNotFound => e
                logger.error 'DC not found'
                return 404
            end
            popUrls = getPopUrls(dc)
            compute_url = popUrls[:compute]
            admin_credentials, errors = authenticate_anella(popUrls[:keystone], dc["tenant_name"], dc['user'], dc['password'])
            tenant_id = admin_credentials[:tenant_id]
            auth_token = admin_credentials[:token]
            begin
                response = RestClient.get compute_url +"/#{tenant_id}/flavors/detail", 'X-Auth-Token' => auth_token, :accept => :json
            rescue Errno::ECONNREFUSED
                # halt 500, 'VIM unreachable'
                logger.error "VIM unreachable"
            rescue RestClient::ResourceNotFound
                logger.error 'Already removed from the VIM.'
                return 404
            rescue => e
                logger.error e
                #logger.error e.response
                return
                # halt e.response.code, e.response.body
            end
            response
        end
    end

    # @method get_pops_dc_id
    # @overload get '/pops/dc/:id'
    #  Returns a DC
    get '/dc/:id' do |id|
        begin
            dc = Dc.find(id.to_i)
        rescue Mongoid::Errors::DocumentNotFound => e
            logger.error 'DC not found'
            return 404
        end
        urls = getPopUrls(dc)
        dc['orch'] = urls[:orch]
        return dc.to_json
    end

    # @method get_pops_dc
    # @overload get '/pops/dc/:id'
    #  Returns a DCs
    get '/dcs' do
        return getDcsTokens()
    end

    # @method get_pops_dc_name
    # @overload get '/pops/dc/name/:name'
    #  Returns a DC given a name
    get '/dc/name/:name' do |name|
        begin
            dc = Dc.find_by(name: name)
        rescue Mongoid::Errors::DocumentNotFound => e
            logger.error 'DC not found'
            return 404
        end
        return dc.to_json
    end

    # @method post_pops_dc
    # @overload post '/pops/dc'
    #  Returns if the DC is correct inserted
    post '/dc' do
        return 415 unless request.content_type == 'application/json'
        pop_info, errors = parse_json(request.body.read)
        puts pop_info
        serv = {
            name: pop_info['name'],
            host: pop_info['host'],
            user: pop_info['user'],
            password: pop_info['password'],
            tenant_name: pop_info['tenant_name'],
            is_admin: pop_info['is_admin'],
            description: pop_info['description'],
            extra_info: pop_info['extra_info'],
            keystone_endpoint: pop_info['keystone_endpoint'],
            neutron_endpoint: pop_info['neutron_endpoint'],
            glance_endpoint: pop_info['glance_endpoint'],
            nova_endpoint: pop_info['nova_endpoint'],
            heat_endpoint: pop_info['heat_endpoint'],
            dns: pop_info['dns']
        }
        begin
            dc = Dc.find_by(name: pop_info['name'])
            halt 409, 'DC Duplicated. Use PUT for update.'
        # i es.update_attributes!(:host => pop_info['host'], :port => pop_info['port'], :token => @token, :depends_on => serv_reg['depends_on'])
        rescue Mongoid::Errors::DocumentNotFound => e
            begin
                dc = Dc.create!(serv)
            rescue => e
                puts 'ERROR.................'
                puts e
            end
        rescue => e
            puts e
            logger.error 'Error saving dc.'
            halt 400
        end

        halt 201, { id: dc._id }.to_json
    end

    put '/dc/:id' do |id|
        return 415 unless request.content_type == 'application/json'
        pop_info, errors = parse_json(request.body.read)

        begin
            dc = Dc.find(id.to_i)
        rescue Mongoid::Errors::DocumentNotFound => e
            logger.error 'DC not found'
            return 404
        end

        dc.update_attributes(pop_info)

        halt 200
    end

    # @method delete_pops_dc_id
    # @overload delete '/pops/dc/:id'
    #  Delete a DC
    delete '/dc/:id' do |id|
        begin
            Dc.find(id.to_i).destroy
        rescue Mongoid::Errors::DocumentNotFound => e
            halt 404
        end
        halt 200
    end

end

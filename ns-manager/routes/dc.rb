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


    # @method get_ns_flavours
    # @overload get "/get_list_flavours/:id"
    # Get the flavours avaliable for the sercice
    get '/get_list_flavours/:id' do |id|
        begin
            begin
                dc = Dc.find(id.to_i)
            rescue Mongoid::Errors::DocumentNotFound => e
                logger.error 'DC not found'
                return 404
            end
            return dc.to_json
            # instance = Nsr.find(params['id'])
            # vim_info = {
            #     'keystone' => instance['authentication'][0]['urls']['keystone'],
            #     'tenant' => instance['authentication'][0]['tenant_name'],
            #     'username' => instance['authentication'][0]['username'],
            #     'password' => instance['authentication'][0]['password'],
            #     'heat' => instance['authentication'][0]['urls']['orch'],
            #     'compute' => instance['authentication'][0]['urls']['compute'],
            #     'tenant_id' => instance['authentication'][0]['tenant_id']
            # }
            # token_info = request_auth_token(vim_info)
            # auth_token = token_info[0]['access']['token']['id'].to_s
            # #credentials, errors = authenticate(vim_info['keystone'], vim_info['password'], vim_info['username'], vim_info['password'])
            # tenant_id = vim_info['tenant_id']
            # compute_url = vim_info['compute']
            # query_params = ""
            # flavors = JSON.parse(get_list_flavors(compute_url, tenant_id, query_params, auth_token))
        end
    end

    # @method get_pops_dc_id
    # @overload get '/pops/dc/:id'
    #  Returns a DC
    get '/dc/:id' do |id|
        puts Dc.all.to_json
        begin
            dc = Dc.find(id.to_i)
        rescue Mongoid::Errors::DocumentNotFound => e
            logger.error 'DC not found'
            return 404
        end
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
        serv = {
            name: pop_info['name'],
            host: pop_info['host'],
            user: pop_info['user'],
            password: pop_info['password'],
            tenant_name: pop_info['tenant_name'],
            is_admin: pop_info['is_admin'],
            description: pop_info['description'],
            extra_info: pop_info['extra_info']
        }
        logger.debug serv
        begin
            dc = Dc.find_by(name: pop_info['name'])
            halt 409, 'DC Duplicated. Use PUT for update.'
        # i es.update_attributes!(:host => pop_info['host'], :port => pop_info['port'], :token => @token, :depends_on => serv_reg['depends_on'])
        rescue Mongoid::Errors::DocumentNotFound => e
            begin
                puts serv
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

    put '/services' do
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

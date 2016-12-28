# -*- coding: utf-8 -*-
#
# TeNOR - NS Provisioning
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
# @see NsProvisioning
class Provisioner < NsProvisioning
    # @method get_ns_instances
    # @overload get "/ns-instances"
    # Gets all ns-instances
    get '/' do
        #logger.info 666,'Getting NS instances.'
        instances = if params[:status]
                        Nsr.where(status: params[:status])
                    else
                        Nsr.all
                       end

        return instances.to_json
    end

    # @method get_ns_instance_id
    # @overload get "/ns-instances/:id"
    # Get a ns-instance
    get '/:id' do
        begin
            # Retrieves deep info on VMs (IPs and States)
            # def authenticate_anella(keystone_url, tenant_name, username, password)
            instance = Nsr.find(params['id'])
            pop_urls = instance['authentication'][0]['urls']
            dc = {
                'tenant_name' => instance['authentication'][0]['tenant_name'],
                'user' => instance['authentication'][0]['username'],
                'password' => instance['authentication'][0]['password']
            }
            operationId = id
            admin_credentials, errors = authenticate_anella(pop_urls['keystone'], dc["tenant_name"], dc['user'], dc['password'])
            puts admin_credentials
            tenant_id = admin_credentials[:tenant_id]
            auth_token = admin_credentials[:token]

            instance['vnfrs'].each do |vnf|
                response = JSON.parse(RestClient.get settings.vnf_manager + '/vnf-provisioning/vnf-instances/' + vnf['vnfr_id'],:accept => :json)
                response['vms'].each do |vm|
                    vnf['vnf_id'] = { 'openstack_id': vm['physical_resource_id'] }
                    url = 
                        pop_urls['compute']+'/'+
                        tenant_id+
                        '/servers/'+vm['physical_resource_id']
                    begin
                        check = RestClient.get(url, headers = {'X-Auth-Token' => auth_token,'accept' => 'json'})
                        data = JSON.parse(check.body)
                        vnf['server'] = { 'status': data['server']['status'], 'addresses': [] }
                        data['server']['addresses'].each do |ad|
                            vnf['server']['addresses'].append(ad)
                        end
                    rescue => e
                        logger.error operationId, 'Openstack request failed',id
                        halt e.response.code, e.response
                    end
                end
            end
        rescue Mongoid::Errors::DocumentNotFound => e
            halt 404
        end
        return instance.to_json
    end

    # @method post_ns_instances
    # @overload post '/ns'
    # Instantiation request
    # @param [JSON]
    # Request body: {"nsd": "descriptor", "customer_id": "some_id", "nap_id": "some_id"}'
    post '/' do
        # Return if content-type is invalid
        return 415 unless request.content_type == 'application/json'
        # Validate JSON format
        instantiation_info, errors = parse_json(request.body.read)
        return 400, errors.to_json if errors

        nsd = instantiation_info['nsd']

        if instantiation_info['flavour'].nil?
            halt 400, 'Failed creating instance. Flavour is null'
        end

        instance = {
            nsd_id: nsd['id'],
            descriptor_reference: nsd['id'],
            auto_scale_policy: nsd['auto_scale_policy'],
            connection_points: nsd['connection_points'],
            monitoring_parameters: nsd['monitoring_parameters'],
            service_deployment_flavour: instantiation_info['flavour'],
            public_network_id: instantiation_info['public_network_id'],
            vendor: nsd['vendor'],
            version: nsd['version'],
            # vlr
            vnfrs: [],
            lifecycle_events: nsd['lifecycle_events'],
            vnf_depedency: nsd['vnf_depedency'],
            vnffgd: nsd['vnffgd'],
            # pnfr
            resource_reservation: [],
            runtime_policy_info: [],
            status: 'INIT',
            notification: instantiation_info['callback_url'],
            lifecycle_event_history: ['INIT'],
            audit_log: [],
            marketplace_callback: instantiation_info['callback_url'],
            authentication: []
        }

        @instance = Nsr.new(instance)
        @instance.save!
        operationId = @instance.id
        logger.info operationId, 'Instanciating NS instance.'
        # call thread to process instantiation
        Thread.new do
            instantiate(@instance, nsd, instantiation_info)
        end

        return 201, @instance.to_json
    end

    # @method put_ns_instance_id
    # @overload put '/ns-instances/:ns_instance_id'
    # NS Instance update request
    # @param [JSON]
    put '/:ns_instance_id' do
    end

    # @method get_ns_instance_status
    # @overload gett '/ns-instances/:nsr_id/status'
    # Get instance status
    # @param [JSON]
    get '/:nsr_id/status' do
        begin
            instance = Nsr.find(params[:nsr_id])
        rescue Mongoid::Errors::DocumentNotFound => e
            halt 404
        end

        return instance['status']
    end

    # @method put_ns_instance_status
    # @overload post '/ns-instances/:nsr_id/status'
    # Update instance status
    # @param [JSON]
    put '/:id/:status' do
        body, errors = parse_json(request.body.read)
        @instance = body['instance']
        begin
            @nsInstance = Nsr.find(params['id'])
        rescue Mongoid::Errors::DocumentNotFound => e
            halt 404
        end
        operationId = @nsInstance.id
        vim_info = {
            'tenant_name' => @nsInstance['authentication'][0]['tenant_name'],
            'user' => @nsInstance['authentication'][0]['username'],
            'password' => @nsInstance['authentication'][0]['password'],
            'pop_urls' => @nsInstance['authentication'][0]['urls']
        }
        if params[:status] === 'terminate'
            logger.info operationId, 'Starting thread for removing VNF and NS instances.'
            @nsInstance.update_attribute('status', 'DELETING')
            Thread.abort_on_exception = false
            Thread.new do
                # operation = proc {
                @nsInstance['vnfrs'].each do |vnf|
                    logger.info operationId, 'Terminate VNF ' + vnf['vnfr_id'].to_s
                    logger.info operationId, 'Pop_id: ' + vnf['pop_id'].to_s
                    raise 'VNF not defined' if vnf['pop_id'].nil?

                    pop_info, errors = getPopInfo(vnf['pop_id'])
                    logger.error operationId, errors if errors
                    raise 400, errors if errors

                    if pop_info == 400
                        logger.error operationId, 'Pop id no exists.'
                        return
                    end

                    pop_auth = @nsInstance['authentication'].find { |pop| pop['pop_id'] == vnf['pop_id'] }
                    popUrls = pop_auth['urls']
                    callback_url = settings.manager + '/ns-instances/' + @instance['id']

                    next if vnf['vnfr_id'].nil?
                    # get token
                    credentials, errors = authenticate(popUrls[:keystone], pop_auth['tenant_name'], pop_auth['username'], pop_auth['password'])
                    logger.error operationId, errors if errors
                    return if errors
                    auth = { auth: { tenant_id: credentials[:tenant_id], user_id: credentials[:user_id], token: credentials[:token], url: { keystone: popUrls[:keystone] } }, callback_url: callback_url }
                    begin
                        response = RestClient.post settings.vnf_manager + '/vnf-provisioning/vnf-instances/' + vnf['vnfr_id'] + '/destroy', auth.to_json, content_type: :json
                    rescue Errno::ECONNREFUSED, Errno::EHOSTUNREACH
                    # halt 500, 'VNF Manager unreachable'
                    rescue RestClient::ResourceNotFound
                        puts 'Already removed from the VIM.'
                        logger.error operationId, 'Already removed from the VIM.'
                    rescue RestClient::ServerBrokeConnection
                        logger.error operationId, 'VNF Manager brokes the connection due timeout.'
                        return
                    rescue => e
                        puts 'Probably an error with mAPI'
                        puts e
                        logger.error operationId, e
                        logger.error operationId, e.response
                        # halt e.response.code, e.response.body
                    end
                end

                logger.info operationId, 'VNFs removed correctly.'
                error = 'Removing instance'
                recoverState(@nsInstance, error)
            end
            errback = proc do
                logger.error operationId, 'Error with the removing process...'
            end
            callback = proc do
                logger.info operationId, 'Removing finished correctly.'
            end
        elsif params[:status] === 'start'
            @instance['vnfrs'].each do |vnf|
                logger.info operationId, 'Starting VNF ' + vnf['vnfr_id'].to_s
                event = { event: 'start', vim_info: vim_info }
                endpoint = '/config'
                begin
                    response = RestClient.put settings.vnf_manager + '/vnf-provisioning/vnf-instances/' + vnf['vnfr_id'] + endpoint, event.to_json, content_type: :json
                rescue Errno::ECONNREFUSED
                    logger.error operationId, 'VNF Manager unreachable.'
                    halt 500, 'VNF Manager unreachable'
                rescue => e
                    logger.error operationId, e.response
                    halt e.response.code, e.response.body
                end
                @nsInstance.push(lifecycle_event_history: 'Executed a start')
            end

            @instance['status'] = params['status'].to_s.upcase
            @nsInstance.update_attributes(@instance)
        elsif params[:status] === 'stop'
            @instance['vnfrs'].each do |vnf|
                logger.debug vnf
                event = { event: 'stop', vim_info: vim_info }
                endpoint = '/config'
                begin
                    response = RestClient.put settings.vnf_manager + '/vnf-provisioning/vnf-instances/' + vnf['vnfr_id'] + endpoint, event.to_json, content_type: :json
                rescue Errno::ECONNREFUSED
                    logger.error operationId, 'VNF Manager unreachable.'
                    halt 500, 'VNF Manager unreachable'
                rescue => e
                    logger.error operationId, e.response
                    halt e.response.code, e.response.body
                end
            end
            
            @instance['status'] = params['status'].to_s.upcase
            @nsInstance
        end

        halt 200
    end

    get '/ns-instances-mapping' do
    end

    post '/ns-instances-mapping' do
    end

    delete '/ns-instances-mapping/:id' do
    end

    # @method post_ns_instances_id_instantiate
    # @overload post '/ns-instances/:id/instantiate'
    # Response from VNF-Manager, send a message to marketplace
    post '/:nsr_id/instantiate' do
        operationId = params['nsr_id'].to_s
        logger.info operationId, 'Instantiation response about ' + params['nsr_id'].to_s
        # Return if content-type is invalid
        return 415 unless request.content_type == 'application/json'
        # Validate JSON format
        response, errors = parse_json(request.body.read)
        return 400, errors.to_json if errors

        callback_response = response['callback_response']
        @instance = response['instance']
        operationId = @instance.id
        begin
            instance = Nsr.find(@instance['id'])
        rescue Mongoid::Errors::DocumentNotFound => e
            logger.error operationId, e
            return 404
        end
        nsd = response['nsd']
        nsr_id = params['nsr_id']

        if callback_response['status'] == 'ERROR_CREATING'
            @instance['status'] = 'ERROR_CREATING'
            @instance['lifecycle_event_history'].push('ERROR_CREATING')
            @instance['audit_log'].push(callback_response['stack_resources']['stack']['stack_status_reason'])
            instance.update_attributes(@instance)
            generateMarketplaceResponse(@instance['notification'], { status: 'error', message: callback_response['stack_resources']['stack']['stack_status_reason'] }.to_s)
            return 200
        end

        logger.info operationId, callback_response['vnfd_id'].to_s + ' INSTANTIATED'

        @instance['lifecycle_event_history'].push('VNF ' + callback_response['vnfd_id'].to_s + ' INSTANTIATED')
        @vnfr = @instance['vnfrs'].find { |vnf_info| vnf_info['vnfd_id'] == callback_response['vnfd_id'] }
        @vnfr['vnfi_id'] = callback_response['vnfi_id']
        @vnfr['status'] = 'INSTANTIATED'
        @vnfr['vnf_addresses'] = callback_response['vnf_addresses']

        instance.update_attributes(@instance)

        # for each VNF instantiated, read the connection point in the NSD and extract the resource id
        logger.error operationId, 'VNFR Stack Resources: ' + callback_response['stack_resources'].to_s
        vnfr_resources = callback_response['stack_resources']
        nsd['vld']['virtual_links'].each do |vl|
            vl['connections'].each do |conn|
                vnf_net = conn.split('#')[1]
                vnf_id = vnf_net.split(':')[0]
                net = vnf_net.split(':ext_')[1]

                next unless vnf_id == vnfr_resources['vnfd_reference']
                logger.info operationId, 'Searching ports for network ' + net.to_s
                next if net == 'undefined'
                vlr = vnfr_resources['vlr_instances'].find { |vlr| vlr['alias'] == net }
                logger.info operationId, vnfr_resources['port_instances']
                logger.info operationId, vlr
                next unless !vnfr_resources['port_instances'].empty? && !vlr.nil?
                vnf_ports = vnfr_resources['port_instances'].find_all { |port| port['vlink_ref'] == vlr['id'] }
                ports = {
                    ns_network: conn,
                    vnf_ports: vnf_ports
                }
                resources = @instance['resource_reservation'].find { |res| res['pop_id'] == @vnfr['pop_id'] }
                resources['ports'] << ports
                instance.update_attributes(@instance)
            end
        end

        logger.info operationId, 'Checking if all the VNFs are instantiated.'
        nsd['vnfds'].each do |vnf|
            vnf_instance = @instance['vnfrs'].find { |vnf_info| vnf_info['vnfd_id'] == vnf }
            if vnf_instance['status'] != 'INSTANTIATED'
                logger.info operationId, 'VNF ' + vnf.to_s + ' is not ready.'
                return
            end
        end

        logger.info operationId, 'Service is ready. All VNFs are instantiated'
        @instance['status'] = 'INSTANTIATED'
        @instance['lifecycle_event_history'].push('INSTANTIATED')
        @instance['instantiation_end_time'] = DateTime.now.iso8601(3)
        instance.update_attributes(@instance)

        generateMarketplaceResponse(@instance['notification'], @instance)
        logger.info operationId, 'Marketplace is notified'

        logger.info operationId, 'Sending statistic information to NS Manager'
        Thread.new do
            begin
                RestClient.post settings.manager + '/statistics/performance_stats', @instance.to_json, content_type: :json
            rescue => e
                logger.error operationId, e
            end
        end

        logger.info operationId, 'Sending start command'
        Thread.new do
            sleep(5)
            begin
                RestClient.put settings.manager + '/ns-instances/' + nsr_id + '/start', {}.to_json, content_type: :json
            rescue Errno::ECONNREFUSED
                logger.error operationId, 'Connection refused with the NS Manager'
            rescue => e
                logger.error operationId, e.response
                logger.error operationId, 'Error with the start command'
            end
        end

        if @instance['resource_reservation'].find { |resource| resource.has_key?('wicm_stack')}
            logger.info operationId, 'Starting traffic redirection in the WICMi'
            Thread.new do
                begin
                    response = RestClient.put settings.wicm + '/vnf-connectivity/' + nsr_id, '', content_type: :json, accept: :json
                rescue => e
                    logger.error operationId, e
                end
                logger.info operationId, response
            end
        end

        logger.info operationId, 'Starting monitoring workflow...'
        Thread.new do
            sleep(5)
            monitoringData(nsd, nsr_id, @instance)
        end

        unless settings.netfloc.nil?
            logger.info operationId, 'Create Netfloc HOT for each PoP'

            chains_pop = []
            instance['vnffgd']['vnffgs'].each do |fg|
                fg['network_forwarding_path'].each do |path|
                    path['connection_points'].each do |port|
                        resource = instance['resource_reservation'].find { |resource| resource['ports'].find { |p| p['ns_network'] == port } }
                        vnf_port = resource['ports'].find { |p| p['ns_network'] == port }
                        if chains_pop.detect { |chain| chain[:pop_id] == resource['pop_id'].to_s }.nil?
                            chains_pop << { pop_id: resource['pop_id'].to_s, ports: [] }
                            chains_pop.find { |chain| chain[:pop_id] == resource['pop_id'].to_s }[:ports] << vnf_port['vnf_ports'][0]['physical_resource_id']
                        else
                            chains_pop.find { |chain| chain[:pop_id] == resource['pop_id'].to_s }[:ports] << vnf_port['vnf_ports'][0]['physical_resource_id']
                        end
                    end
                end
            end

            chains_pop.each do |chain|
                # get credentials for each PoP
                pop_auth = @instance['authentication'].find { |pop| pop['pop_id'] == chain[:pop_id] }
                popUrls = pop_auth['urls']
                tenant_token = openstackAuthentication(popUrls['keystone'], pop_auth['tenant_id'], pop_auth['username'], pop_auth['password'])

                # generate netfloc hot template for a chain
                hot_generator_message = {
                    ports: chain[:ports],
                    odl_username: settings.odl_username,
                    odl_password: settings.odl_password,
                    netfloc_ip_port: settings.netfloc
                }

                logger.info operationId, 'Generating network HOT template...'
                hot_template, errors = generateNetflocTemplate(hot_generator_message)
                logger.error operationId, 'Error generating Netfloc template.' if errors
                return 400, errors.to_json if errors

                logger.info operationId, 'Send Netfloc HOT to Openstack'
                stack_name = 'Netfloc_' + @instance['id'].to_s
                template = { stack_name: stack_name, template: hot_template }
                stack, errors = sendStack(popUrls['orch'], pop_auth['tenant_id'], template, tenant_token)
                logger.error operationId, 'Error sending Netfloc template to Openstack.' if errors
                logger.error operationId, errors if errors
                return 400, errors.to_json if errors

                logger.debug stack
            end
        end

        return 200
    end
end

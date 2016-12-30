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
# @see TnovaManager
module VimHelper

  def authentication_v2(pop_info, extrainfo)

        auth = { auth: { tenantName: extrainfo[:tenantname], passwordCredentials: { username: pop_info['adminid'], password: pop_info['password'] } } }
        begin
            response = RestClient.post extrainfo[:keystone] + '/tokens', auth.to_json, content_type: :json
        rescue Errno::ECONNREFUSED => e
            return 500, 'Connection refused'
        rescue RestClient::ExceptionWithResponse => e
            logger.error e
            logger.error e.response.body
            return e.response.code, e.response.body
        rescue => e
            logger.error e
            logger.error e.response.body
            return 400, errors if errors
        end
        return parse_json(response)
  end

  # Authetication_v2_anella
  def authentication_v2_anella(keystoneUrl, tenant_name, user, password)
    auth = { auth: { tenantName: tenant_name, passwordCredentials: { username: user, password: password } } }
    begin
      response = RestClient.post keystoneUrl + '/tokens', auth.to_json, content_type: :json
    rescue => e
      logger.error e
      logger.error e.response.body
      return 400, e
    end
    return parse_json(response)
  end


  # Authetication_v3_anella
  def authentication_v3_anella(keystoneUrl, tenant_name, user, password)
    auth = {
        "auth": {
             "identity": {
                "methods": [
                    "password"
                ],
                "password": {
                    "user": {
                        "name": user,
                        "domain": {
                             "name": tenant_name
                        },
                        "password": password
                    }
                }
            }
        }
    }
    begin
      response = RestClient.post keystoneUrl + "/auth/tokens" , auth.to_json, {:content_type => :json, :accept => :json}
    rescue => e
      logger.error "failure to auth3"
      logger.error e 
      logger.error e.response.body
      return 400, e, e
    end
    return response, response.headers
  end



  # Authenticate method for Anella
  def authenticate_anella(keystone_url, tenant_name, username, password)
    keystone_version = URI(keystone_url).path.split('/').last
    if keystone_version == 'v2.0'
      user_authentication, errors = authentication_v2_anella(keystone_url, tenant_name, username, password)
      logger.error errors if errors
      return 400, errors.to_json if errors
      tenant_id = user_authentication['access']['token']['tenant']['id']
      user_id = user_authentication['access']['user']['id']
      token = user_authentication['access']['token']['id']
    elsif keystone_version == 'v3'
      user_authentication, headers, errors = authentication_v3_anella(keystone_url, tenant_name, username, password)
      logger.error errors if errors
      return 400, errors.to_json if errors
      user_authentication = JSON.parse(user_authentication.body)
      project = user_authentication['token']['project']
      if !project.nil?
        tenant_id = user_authentication['token']['project']['id']
        user_id = user_authentication['token']['user']['id']
        token = headers[:x_subject_token] #  user_authentication['token']['id']
      else
        errors = "No project found with the authentication."
        return 400, errors.to_json if errors
      end
    end
    {:tenant_id => tenant_id, :user_id => user_id, :token => token}
  end

  def authentication_v3(pop_info, extrainfo)

    auth = {
      auth: {
        identity: {
          methods: ['password'],
          password: {
            user:{
              name: pop_info['adminid'],
              domain: { "name": extrainfo[:tenantname] },
              password: pop_info['password']
            }
          }
        }
      }
    }
    begin
        response = RestClient.post extrainfo[:keystone] + '/auth/tokens', auth.to_json, content_type: :json
    rescue Errno::ECONNREFUSED => e
        return 500, 'Connection refused'
    rescue RestClient::ExceptionWithResponse => e
        logger.error e
        logger.error e.response.body
        return e.response.code, e.response.body
    rescue => e
        logger.error e
        logger.error e.response.body
        return 400, errors if errors
    end
    return parse_json(response)
  end

end

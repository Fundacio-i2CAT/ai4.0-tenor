# -*- coding: utf-8 -*-
#
# TeNOR - VNF Provisioning
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
# Convert BSON ID to String
module BSON
    class ObjectId
        def to_json(*args)
            to_s.to_json
        end

        def as_json(*args)
            to_s.as_json
        end
    end
end

class Cachedimg
    include Mongoid::Document
    include Mongoid::Timestamps

    field :stack_url, type: String
    field :image_url, type: String
    field :openstack_id, type: String
    field :vim_url, type: String
end

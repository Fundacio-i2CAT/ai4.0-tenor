require 'autoinc'

module BSON
  class ObjectId
    def to_json(*)
      to_s.to_json
    end
    def as_json(*)
      to_s.as_json
    end
  end
end

module Mongoid
  module Document
    def serializable_hash(options = nil)
      h = super(options)
      h['id'] = h.delete('_id') if(h.has_key?('_id'))
      #h['password'] = "******" if(h.has_key?('password'))
      h
    end
  end
end

class Dc
    include Mongoid::Document
     include Mongoid::Autoinc

    field :name, type: String
    validates :name, presence: true, uniqueness: true
    field :host, type: String
    field :user, type: String
    field :password, type: String
    field :tenant_name, type: String
    field :is_admin, type: Boolean
    field :extra_info, type: String
    field :keystone_endpoint, type: String
    field :nova_endpoint, type: String
    field :glance_endpoint, type: String
    field :heat_endpoint, type: String
    field :neutron_endpoint, type: String
    field :dns, type: String
    field :description, type: String
    increments :id
end

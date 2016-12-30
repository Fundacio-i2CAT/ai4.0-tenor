# Orquestrador Plataforma Anella Industrial 4.0

## Requirements

[TeNOR SEG-version](https://stash.i2cat.net/projects/AI40/repos/tenor/browse) installed and running

## Start:

```
$ virtualenv venv
$ source venv/bin/activate
(venv) $ python start.py
```

## Register a VNF

See [ovnf_example.json](tenor_client/samples/ovnf_example.json)

```
curl -XPOST http://localhost:8082/orchestrator/api/v0.1/vnf -H "Content-Type: application/json" --data-binary @tenor_client/samples/ovnf_example.json
```

```
{
    "state": "PROVISIONED",
    "vnf_id": 1899
}
```

## Register a NS related to the VNF id in ons_example.json

See [ons_example.json](tenor_client/samples/ons_example.json)

```
curl -XPOST http://localhost:8082/orchestrator/api/v0.1/ns -H "Content-Type: application/json" --data-binary @tenor_client/samples/ons_example.json
```

```
{
    "state": "PROVISIONED",
    "ns_id": 1899
}
```

## Instantiate the Network Service providing consumer configuration in onsi_example.json

See [onsi_example.json](tenor_client/samples/onsi_example.json)

```
curl -XPOST http://localhost:8082/orchestrator/api/v0.1/ns/1899 -H "Content-Type: application/json" --data-binary @tenor_client/samples/onsi_example.json
```

```
{
    "service_instance_id": "581c43c1df67b55665000003",
    "state": "PROVISIONED"
}
```


## Post a new service creating new VNF, NS and NSI in a single round (see [example json file](tenor_client/samples/another.json))

```
$ curl -XPOST http://localhost:8082/orchestrator/api/v0.1/service/instance -H "Content-Type: application/json" --data-binary @tenor_client/samples/catalog_v4.json
```


```
{"state": "PROVISIONED", "id": "580f12c7df67b515c8000007"}
```


## List all services deployed


```
$ curl -XGET http://localhost:8082/orchestrator/api/v0.1/service/instance
```

```
[
    {
        "ns_instance_id": "580f130edf67b515c8000008",
        "state": "PROVISIONED"
    },
    {
        "ns_instance_id": "580f0647df67b515c8000005",
	 "runtime_params": [
            {
                "desc": "Service instance IP address", 
                "name": "instance_ip", 
                "value": "172.24.4.168"
            }
        ], 
        "addresses": [
            {
                "OS-EXT-IPS:type": "fixed",
                "addr": "192.85.141.3"
            },
            {
                "OS-EXT-IPS:type": "floating",
                "addr": "172.24.4.168"
            },
        ],
        "state": "RUNNING"
    }
]
```

## List one service by its id

```
$ curl -XGET http://localhost:8082/orchestrator/api/v0.1/service/instance/580f064bdf67b515c8000006
```

```
{
    "ns_instance_id": "580f064bdf67b515c8000006",
    "runtime_params": [
        {
            "desc": "Service instance IP address", 
            "name": "instance_ip", 
            "value": "172.24.4.168"
        }
    ], 
    "addresses": [
        {
            "OS-EXT-IPS:type": "fixed",
            "addr": "192.150.153.3"
        },
        {
            "OS-EXT-IPS:type": "floating",
            "addr": "172.24.4.168"
        }
    ],
    "state": "DEPLOYED"
}
```

## Start/Stop a service

```
$ curl -XPUT http://localhost:8082/orchestrator/api/v0.1/service/instance/580f064bdf67b515c8000006 -H "Content-Type: application/json" --data '{"state": "running"}'
200
{
    "message": "Successfully sent state signal"
}
$ curl -XPUT http://localhost:8082/orchestrator/api/v0.1/service/instance/580f064bdf67b515c8000006 -H "Content-Type: application/json" --data '{"state": "running"}'
200
{
    "message": "Successfully sent state signal"
}
$ curl -XPUT http://localhost:8082/orchestrator/api/v0.1/service/instance/580f064bdf67b515c8000006 -H "Content-Type: application/json" --data '{"state": "deployed"}'
409
{
    "message": "Conflict: 580f064bdf67b515c8000006 stopped(running)"
}
```

## Get PoPs available

```
$ curl -XGET http://localhost:8082/orchestrator/api/v0.1/pop
200
[
    {
        "name": "infrRepository-Pop-ID", 
        "pop_id": 9
    }, 
    {
        "name": "infrRepository-Pop-ID", 
        "pop_id": 1
    }, 
    {
        "name": "Adam", 
        "pop_id": 21
    }
]
```

## Get Flavors available on a PoP


```
$ curl -XGET http://localhost:8082/orchestrator/api/v0.1/pop/21/flavors
200
{
    "flavors": [
        {
            "disk": 50, 
            "name": "VM.M1", 
            "ram": 2048, 
            "vcpus": 2
        }, 
        {
            "disk": 20, 
            "name": "VM.L4", 
            "ram": 12288, 
            "vcpus": 4
        }, 
        {
            "disk": 85, 
            "name": "VM.M6", 
            "ram": 4096, 
            "vcpus": 2
        }, 
        {
            "disk": 25, 
            "name": "VM.S", 
            "ram": 1024, 
            "vcpus": 1
        }
    ]
}
```

## Get Networks available on a PoP


```
$ curl -XGET http://localhost:8082/orchestrator/api/v0.1/pop/21/networks
200
{
    "networks": [
        {
            "id": "d2c87db8-8e6a-499e-86dc-a7022b169f89", 
            "name": "ext-abast_aspy-net", 
            "router_external": true
        }, 
        {
            "id": "06f3db53-56c2-49b6-ab4e-5a8a5c836689", 
            "name": "ext-backup-net", 
            "router_external": true
        }, 
        {
            "id": "88aa11d8-f39d-480f-b048-12660beb2d49", 
            "name": "ext-abast_enuve-net", 
            "router_external": true
        }, 
        {
            "id": "fb2677ae-a502-4d9f-b58a-ba0cfcf40e66", 
            "name": "ext-enisa_integracion-net", 
            "router_external": true
        }
    ]
}
```

## Get Quota sets available on a PoP for the tenant configured in TeNOR


```
$ curl -XGET http://localhost:8082/orchestrator/api/v0.1/pop/21/quotas
200
{
    "quotas": {
        "cores": 20,
        "fixed_ips": -1,
        "floating_ips": 10,
        "id": "579eaa7245d04e778f0effd77565794c",
        "injected_file_content_bytes": 10240,
        "injected_file_path_bytes": 255,
        "injected_files": 5,
        "instances": 10,
        "key_pairs": 100,
        "metadata_items": 128,
        "ram": 51200,
        "security_group_rules": 20,
        "security_groups": 10,
        "server_group_members": 10,
        "server_groups": 10
    }
}
```

## Get server instances on a PoP for the tenant configured in TeNOR


```
$ curl -XGET http://localhost:8082/orchestrator/api/v0.1/pop/21/servers
200
{
    "servers": [
        {
            "OS-DCF:diskConfig": "MANUAL",
            "OS-EXT-AZ:availability_zone": "nova",
            "OS-EXT-SRV-ATTR:host": "ubuntu",
            "OS-EXT-SRV-ATTR:hypervisor_hostname": "ubuntu",
            "OS-EXT-SRV-ATTR:instance_name": "instance-00000887",
            "OS-EXT-STS:power_state": 1,
            "OS-EXT-STS:task_state": null,
            "OS-EXT-STS:vm_state": "active",
            "OS-SRV-USG:launched_at": "2016-12-29T11:48:08.000000",
            "OS-SRV-USG:terminated_at": null,
            "accessIPv4": "",
            "accessIPv6": "",
            "addresses": {
                "management": [
                    {
                        "OS-EXT-IPS-MAC:mac_addr": "fa:16:3e:4f:63:37",
                        "OS-EXT-IPS:type": "fixed",
                        "addr": "192.83.221.3",
                        "version": 4
                    },
                    {
                        "OS-EXT-IPS-MAC:mac_addr": "fa:16:3e:4f:63:37",
                        "OS-EXT-IPS:type": "floating",
                        "addr": "172.24.4.94",
                        "version": 4
                    }
                ]
            },
            "config_drive": "True",
            "created": "2016-12-29T11:45:33Z",
            "flavor": {
                "id": "4",
                "links": [
                    {
                        "href": "http://84.88.40.75:8774/277ba4bedd824eabbf26b3ae997f4cbe/flavors/4",
                        "rel": "bookmark"
                    }
                ]
            },
            "hostId": "32d8b4e94ea0c2d8a4880d0b13691e6e8b87336fed4b5bb31edc2253",
            "id": "af2e2fbb-a3e8-4bf0-bd00-5e36f8421c80",
            "image": {
                "id": "d178f602-7d57-402f-a2c3-fc125411a98a",
                "links": [
                    {
                        "href": "http://84.88.40.75:8774/277ba4bedd824eabbf26b3ae997f4cbe/images/d178f602-7d57-402f-a2c3-fc125411a98a",
                        "rel": "bookmark"
                    }
                ]
            },
            "key_name": "UamQ1Ra0U3cU",
            "links": [
                {
                    "href": "http://84.88.40.75:8774/v2.1/277ba4bedd824eabbf26b3ae997f4cbe/servers/af2e2fbb-a3e8-4bf0-bd00-5e36f8421c80",
                    "rel": "self"
                },
                {
                    "href": "http://84.88.40.75:8774/277ba4bedd824eabbf26b3ae997f4cbe/servers/af2e2fbb-a3e8-4bf0-bd00-5e36f8421c80",
                    "rel": "bookmark"
                }
            ],
            "metadata": {},
            "name": "In-form4.0_5864f704df67b5181900000f-vdu0-hotmmvxamnor",
            "os-extended-volumes:volumes_attached": [],
            "progress": 0,
            "security_groups": [
                {
                    "name": "default"
                }
            ],
            "status": "ACTIVE",
            "tenant_id": "277ba4bedd824eabbf26b3ae997f4cbe",
            "updated": "2016-12-29T13:45:11Z",
            "user_id": "675373c1f44647c0926d7999dec67c98"
        }
    ]
}
```

## Get PoP RAM details depending on quota and usage


```
$ curl -XGET http://localhost:8082/orchestrator/api/v0.1/pop/1/ram
200
{
    "ram": {
        "quota": 51200,
        "ratio": 0.16,
        "units": "MB",
        "used": 8192
    }
}
```

## Get PoP Core details depending on quota and usage


```
$ curl -XGET http://localhost:8082/orchestrator/api/v0.1/pop/1/cores
200
{
    "cores": {
        "quota": 20,
        "ratio": 0.2,
        "used": 4
    }
}
```

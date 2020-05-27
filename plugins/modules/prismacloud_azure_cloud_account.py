#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  Copyright 2020 Palo Alto Networks, Inc
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: prismacloud_azure_cloud_account
short_description: Manage an Azure cloud account onboarded to Prisma Cloud.
description:
    - Manage an Azure cloud account onboarded to Prisma Cloud.
author:
    - Garfield Lee Freeman (@shinmog)
version_added: "2.9"
extends_documentation_fragment:
    - paloaltonetworks.prismacloud.fragments.state
options:
    accountId:
        description:
            - Azure account ID.
            - Either the accountId or the name must be specified.
    enabled:
        description:
            - Whether or not the account is enabled.
        type: bool
    clientId:
        description:
            - Application ID registered with Active Directory.
    groupIds:
        description:
            - List of account group IDs to which you are assigning this account.
        type: list
    name:
        description:
            - Name to be used for the account on the Prisma Cloud platform.
            - Must be unique.
            - Either the accountId or the name must be specified.
    key:
        description:
            - Application ID key.
    monitorFlowLogs:
        description:
            - Automatically ingest flow logs.
        type: bool
    tenantId:
        description:
            - Active Directory ID associated with Azure.
    servicePrincipalId:
        description:
            - Unique ID of the service principal object associated with the
              Prisma Cloud application that you create.
'''

EXAMPLES = '''
- name: add azure accont
  prismacloud_azure_cloud_account:
    name: 'foo'
    enabled: true
    cliendId: 'myId'
    key: 'myAppKey'
    tenantId: 'myTenantId'
    servicePrincipalId: 'myServicePrincipalId'
'''

RETURN = '''
changed:
    description: if a change was necessary
    returned: success
    type: bool
before:
    description: the config before this module is invoked
    returned: success
    type: complex
after:
    description: the config after this module is invoked
    returned: success
    type: complex
'''


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.paloaltonetworks.prismacloud.plugins.module_utils import errors
from ansible_collections.paloaltonetworks.prismacloud.plugins.module_utils import prismacloud as pc


def identify(client, name):
    listing = client.get(['cloud', 'name'], {'cloudType': 'azure'})
    for x in listing:
        if x['name'] == name:
            return x['id']


def main():
    module = AnsibleModule(
        argument_spec=dict(
            accountId=dict(),
            enabled=dict(type='bool'),
            clientId=dict(),
            groupIds=dict(type='list'),
            name=dict(),
            key=dict(),
            monitorFlowLogs=dict(type='bool'),
            tenantId=dict(),
            servicePrincipalId=dict(),
            state=pc.state_spec(),
        ),
        required_one_of=[
            ['accountId', 'name'],
        ],
        supports_check_mode=True,
    )

    client = pc.PrismaCloudRequest(module)

    # Variables.
    obj = None
    results = {'changed': False}

    # Retrieve obj details.
    if module.params['accountId'] is not None:
        try:
            obj = client.get(['cloud', 'azure', module.params['accountId']])
        except errors.ObjectNotFoundError:
            pass
    else:
        the_id = identify(client, module.params['name'])
        if the_id is not None:
            obj = client.get(['cloud', 'azure', the_id])

    results['before'] = obj

    if module.params['state'] == 'present':
        fields = ['cloudAccount', 'clientId', 'key', 'monitorFlowLogs', 'tenantId', 'servicePrincipalId']
        ca_fields = ['accountId', 'enabled', 'groupIds', 'name']
        req_obj = {
            'cloudAccount': {
                'accountId': '',
                'enabled': False,
                'groupIds': [],
                'name': '',
            },
            'clientId': '',
            'key': '',
            'monitorFlowLogs': False,
            'tenantId': '',
            'servicePrincipalId': '',
        }
        for field in fields:
            if field == 'cloudAccount':
                for ca_field in ca_fields:
                    if module.params[ca_field] is not None:
                        req_obj[field][ca_field] = module.params[ca_field]
            elif module.params[field] is not None:
                req_obj[field] = module.params[field]

        if obj is None:
            results['changed'] = True
            if not module.check_mode:
                client.post(['cloud', 'azure'], req_obj)
                req_obj['cloudAccount']['accountId'] = identify(client, module.params['name'])
        else:
            for field in fields:
                if obj.get(field) != req_obj.get(field):
                    results['changed'] = True
                    if not req_obj['cloudAccount']['accountId'] and obj is not None:
                        req_obj['cloudAccount']['accountId'] = obj['cloudAccount']['accountId']
                    if not module.check_mode:
                        client.put(['cloud', 'azure', req_obj['cloudAccount']['accountId']], req_obj)
                    break
        results['after'] = req_obj
    elif module.params['state'] == 'absent':
        results['after'] = None
        if obj is not None:
            results['changed'] = True
            if not module.check_mode:
                client.delete(['cloud', 'azure', obj['cloudAccount']['accountId']])

    # Done.
    module.exit_json(**results)


if __name__ == '__main__':
    main()

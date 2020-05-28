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
module: prismacloud_gcp_cloud_account
short_description: Manage an GCP cloud account onboarded to Prisma Cloud.
description:
    - Manage an GCP cloud account onboarded to Prisma Cloud.
author:
    - Garfield Lee Freeman (@shinmog)
version_added: "2.9"
extends_documentation_fragment:
    - paloaltonetworks.prismacloud.fragments.state
options:
    cloudAccount:
        description:
            - Cloud account definition.
        type: complex
        suboptions:
            accountId:
                description:
                    - GCP account ID.
                    - Either the accountId or the name must be specified.
            enabled:
                description:
                    - Whether or not the account is enabled.
                type: bool
            groupIds:
                description:
                    - List of account group IDs to which you are assigning this account.
                type: list
            name:
                description:
                    - Name to be used for the account on the Prisma Cloud platform.
                    - Must be unique.
                    - Either the accountId or the name must be specified.
    compressionEnabled:
        description:
            - Enable flow log compression.
        type: bool
    dataflowEnabledProject:
        description:
            - GCP project for flow log compression.
            - Required if compressionEnabled is "true".
    flowLogStorageBucket:
        description:
            - GCP flow logs storage bucket.
    credentials:
        description:
            - Service account key.
        type: complex
        suboptions:
            type:
                description:
                    - GCP credentials file parameter.
            project_id:
                description:
                    - GCP credentials file parameter.
            private_key_id:
                description:
                    - GCP credentials file parameter.
            private_key:
                description:
                    - GCP credentials file parameter.
            client_email:
                description:
                    - GCP credentials file parameter.
            client_id:
                description:
                    - GCP credentials file parameter.
            auth_uri:
                description:
                    - GCP credentials file parameter.
            token_uri:
                description:
                    - GCP credentials file parameter.
            auth_provider_x509_cert_url:
                description:
                    - GCP credentials file parameter.
            client_x509_cert_url:
                description:
                    - GCP credentials file parameter.
'''

EXAMPLES = '''
- name: add gcp accont
  prismacloud_gcp_cloud_account:
    cloudAccount:
      name: 'foo'
      enabled: true
    credentials: '{{ lookup('file', './gcp_creds.json') | to_json }}'
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
    listing = client.get(['cloud', 'name'], {'cloudType': 'gcp'})
    for x in listing:
        if x['name'] == name:
            return x['id']


def main():
    module = AnsibleModule(
        argument_spec=dict(
            cloudAccount=dict(
                required=True,
                type='dict',
                required_one_of=[
                    ['accountId', 'name'],
                ],
                options=dict(
                    accountId=dict(),
                    enabled=dict(type='bool'),
                    groupIds=dict(type='list'),
                    name=dict(),
                ),
            ),
            compressionEnabled=dict(type='bool'),
            dataflowEnabledProject=dict(),
            flowLogStorageBucket=dict(),
            credentials=dict(
                type='dict',
                options=dict(
                    type=dict(),
                    project_id=dict(),
                    private_key_id=dict(),
                    private_key=dict(),
                    client_email=dict(),
                    client_id=dict(),
                    auth_uri=dict(),
                    token_uri=dict(),
                    auth_provider_x509_cert_url=dict(),
                    client_x509_cert_url=dict(),
                ),
            ),
            state=pc.state_spec(),
        ),
        supports_check_mode=True,
    )

    client = pc.PrismaCloudRequest(module)

    # Variables.
    obj = None
    results = {'changed': False}

    # Retrieve obj details.
    if module.params['cloudAccount']['accountId'] is not None:
        try:
            obj = client.get(['cloud', 'gcp', module.params['cloudAccount']['accountId']])
        except errors.ObjectNotFoundError:
            pass
    else:
        the_id = identify(client, module.params['cloudAccount']['name'])
        if the_id is not None:
            obj = client.get(['cloud', 'gcp', the_id])

    results['before'] = obj

    if module.params['state'] == 'present':
        fields = ['cloudAccount', 'credentials', 'compressionEnabled', 'dataflowEnabledProject', 'flowLogStorageBucket']
        ca_fields = ['accountId', 'enabled', 'groupIds', 'name']
        c_fields = [
            'type', 'project_id', 'private_key_id', 'private_key', 'client_email',
            'client_id', 'auth_uri', 'token_uri',
            'auth_provider_x509_cert_url', 'client_x509_cert_url',
        ]
        req_obj = {
            'cloudAccount': {
                'accountId': '',
                'enabled': False,
                'groupIds': [],
                'name': '',
            },
            "compressionEnabled": false,
            "dataflowEnabledProject": "",
            "flowLogStorageBucket": "",
            "credentials": {
                "type": "",
                "project_id": "",
                "private_key_id": "",
                "private_key": "",
                "client_email": "",
                "client_id": "",
                "auth_uri": "",
                "token_uri": "",
                "auth_provider_x509_cert_url": "",
                "client_x509_cert_url": "",
            },
        }
        for field in fields:
            if field == 'cloudAccount':
                ca = module.params['cloudAccount']
                for ca_field in ca_fields:
                    if ca[ca_field] is not None:
                        req_obj[field][ca_field] = ca[ca_field]
            elif field == 'credentials':
                creds = module.params['credentials']
                for c_field in c_fields:
                    if creds[c_field] is not None:
                        req_obj[field][c_field] = creds[c_field]
            elif module.params[field] is not None:
                req_obj[field] = module.params[field]

        if obj is None:
            results['changed'] = True
            if not module.check_mode:
                client.post(['cloud', 'gcp'], req_obj)
                req_obj['cloudAccount']['accountId'] = identify(client, module.params['cloudAccount']['name'])
        else:
            for field in fields:
                if obj.get(field) != req_obj.get(field):
                    results['changed'] = True
                    if not req_obj['cloudAccount']['accountId'] and obj is not None:
                        req_obj['cloudAccount']['accountId'] = obj['cloudAccount']['accountId']
                    if not module.check_mode:
                        client.put(['cloud', 'gcp', req_obj['cloudAccount']['accountId']], req_obj)
                    break
        results['after'] = req_obj
    elif module.params['state'] == 'absent':
        results['after'] = None
        if obj is not None:
            results['changed'] = True
            if not module.check_mode:
                client.delete(['cloud', 'gcp', obj['cloudAccount']['accountId']])

    # Done.
    module.exit_json(**results)


if __name__ == '__main__':
    main()

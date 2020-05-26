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
module: prismacloud_cloud_account_facts
short_description: Retrieves info on cloud accounts.
description:
    - This module retrieves onboarded cloud accounts.
author:
    - Garfield Lee Freeman (@shinmog)
version_added: "2.9"
extends_documentation_fragment:
    - paloaltonetworks.prismacloud.fragments.facts
options:
    name:
        description:
            - Filter on cloud accounts with this name.
            - Primary param.
    id:
        description:
            - Specific account group ID.
    cloudType:
        description:
            - Filter on cloud accounts with this cloud type.
        choices:
            - aws
            - azure
            - gcp
            - alibaba_cloud
'''

EXAMPLES = '''
- name: get list of cloud accounts
  prismacloud_cloud_account_facts:
    cloudType: 'azure'
    details: true
  register: ans

- debug:
    msg: '{{ ans.listing }}'
'''

RETURN = '''
total:
    description: number of results in the listing
    returned: success
    type: int
listing:
    description: list of results
    returned: success
    type: list
'''


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.paloaltonetworks.prismacloud.plugins.module_utils import prismacloud as pc


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(),
            id=dict(),
            cloudType=dict(choices=['aws', 'azure', 'gcp', 'alibaba_cloud']),
            details=pc.details_spec(),
            search_type=pc.search_type_spec(),
        ),
        supports_check_mode=False,
    )

    client = pc.PrismaCloudRequest(module)

    path = ['cloud', 'name']
    listing = client.get(path)

    results = client.get_facts_from(
        listing,
        'name', ['cloudType', 'id'],
        ['cloud', 'cloudType', 'id'], (1, 2),
    )

    module.exit_json(**results)


if __name__ == '__main__':
    main()

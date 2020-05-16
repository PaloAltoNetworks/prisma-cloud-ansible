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
module: prismacloud_account_group_facts
short_description: Retrieves info on account groups.
description:
    - This module retrieves account group facts.
author:
    - Garfield Lee Freeman (@shinmog)
version_added: "2.9"
extends_documentation_fragment:
    - paloaltonetworks.prismacloud.fragments.facts
options:
    name:
        description:
            - Filter on account groups with this name.
'''

EXAMPLES = '''
- name: get list of account groups
  prismacloud_account_group_facts:
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
            details=pc.details_spec(),
        ),
        supports_check_mode=False,
    )

    client = pc.PrismaCloudRequest(module)

    name = module.params['name']
    details = module.params['details']

    path = ['cloud', 'group']
    listing = client.get(path)

    ans = []
    for x in listing:
        if name is not None and x['name'] != name:
            continue

        val = None
        if details:
            path = ['cloud', 'group', x['id']]
            val = client.get(path)
        else:
            val = pc.hide_details(x, ['name', 'id'])

        ans.append(val)

    module.exit_json(changed=False, total=len(listing), listing=ans)


if __name__ == '__main__':
    main()

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
module: prismacloud_compliance_standard_requirement_facts
short_description: Retrieves info on compliance standard requirements.
description:
    - This module retrieves compliance standard requirement facts.
author:
    - Garfield Lee Freeman (@shinmog)
version_added: "2.9"
extends_documentation_fragment:
    - paloaltonetworks.prismacloud.fragments.facts
options:
    cs_id:
        description:
            - The compliance standard ID.
        required: true
    name:
        description:
            - Filter on compliance standard requirements with this name.
    system_default:
        description:
            - Filter on a specific system default setting.
        type: bool
'''

EXAMPLES = '''
- name: get list of compliance standard requirements
  prismacloud_compliance_standard_requirement_facts:
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
            cs_id=dict(required=True),
            name=dict(),
            system_default=dict(type='bool'),
            details=pc.details_spec(),
        ),
        supports_check_mode=False,
    )

    client = pc.PrismaCloudRequest(module)

    cs_id = module.params['cs_id']
    name = module.params['name']
    system_default = module.params['system_default']
    details = module.params['details']

    path = ['compliance', cs_id, 'requirement']
    listing = client.get(path)

    ans = []
    for x in listing:
        if name is not None and x['name'] != name:
            continue

        if system_default is not None and x['systemDefault'] != system_default:
            continue

        val = None
        if details:
            path = ['compliance', 'requirement', x['id']]
            val = client.get(path)
        else:
            val = pc.hide_details(x, ['name', 'id', 'systemDefault'])

        ans.append(val)

    module.exit_json(changed=False, total=len(listing), listing=ans)


if __name__ == '__main__':
    main()

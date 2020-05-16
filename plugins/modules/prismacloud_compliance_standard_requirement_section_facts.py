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
module: prismacloud_compliance_standard_requirement_section_facts
short_description: Retrieves info on compliance standard requirement sections.
description:
    - This module retrieves compliance standard requirement section facts.
author:
    - Garfield Lee Freeman (@shinmog)
version_added: "2.9"
notes:
    - As this is a facts module, check mode is not supported.
options:
    csr_id:
        description:
            - The compliance standard requirement ID.
        required: true
    section_id:
        description:
            - Filter on the given section ID.
    system_default:
        description:
            - Filter on a specific system default setting.
        type: bool
'''

EXAMPLES = '''
- name: get list of compliance standard requirement sections
  prismacloud_compliance_standard_requirement_section_facts:
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
            csr_id=dict(required=True),
            section_id=dict(),
            system_default=dict(type='bool'),
        ),
        supports_check_mode=False,
    )

    client = pc.PrismaCloudRequest(module)

    csr_id = module.params['csr_id']
    section_id = module.params['section_id']
    system_default = module.params['system_default']

    path = ['compliance', csr_id, 'section']
    listing = client.get(path)

    ans = []
    for x in listing:
        if section_id is not None and x['sectionId'] != section_id:
            continue

        if system_default is not None and x['systemDefault'] != system_default:
            continue

        ans.append(x)

    module.exit_json(changed=False, total=len(listing), listing=ans)


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
  
# Copyright: (c) 2020, Garfield Lee Freeman (@shinmog)


class ModuleDocFragment(object):
    # Standard files documentation fragment
    DOCUMENTATION = r'''
'''

    FACTS = r'''
notes:
    - As this is a facts module, check mode is not supported.
options:
    details:
        description:
            - Whether to retrieve full detailed results or not.
        type: bool
        default: false
'''

    STATE = r'''
options:
    state:
        description:
            - The state.
        type: str
        default: 'present'
        choices:
            - present
            - absent
'''

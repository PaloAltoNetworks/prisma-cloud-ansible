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
    search_type:
        description:
            - How to interpret the value given for the primary param.
        choices:
            - exact
            - substring
            - regex
        default: 'exact'
    details:
        description:
            - Whether to retrieve full detailed results or not.
        type: bool
        default: false
'''

    FACTS_WITHOUT_DETAILS = r'''
notes:
    - As this is a facts module, check mode is not supported.
options:
    search_type:
        description:
            - How to interpret the value given for the primary param.
        choices:
            - exact
            - substring
            - regex
        default: 'exact'
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

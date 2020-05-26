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


import re

from ansible_collections.paloaltonetworks.prismacloud.plugins.module_utils import errors
from ansible.module_utils._text import to_text
from ansible.module_utils.connection import Connection
from ansible.module_utils.connection import ConnectionError
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.urls import CertificateError


class PrismaCloudRequest(object):
    def __init__(self, module):
        self.module = module
        self.connection = Connection(self.module._socket_path)

    def send_request(self, method, path, query=None, data=None):
        try:
            ans = self.connection.send_request(
                method, path, query, data,
            )
        except ConnectionError as e:
            self.module.fail_json(msg="connection error occurred: {0}".format(e))
        except CertificateError as e:
            self.module.fail_json(msg="certificate error occurred: {0}".format(e))
        except ValueError as e:
            self.module.fail_json(msg="certificate not found: {0}".format(e))
        except errors.ObjectNotFoundError:
            raise
        except errors.PrismaCloudError as e:
            self.module.fail_json(msg='{0}'.format(e))

        return ans

    def post(self, path, query=None, data=None):
        return self.send_request('POST', path, query, data)

    def get(self, path, query=None):
        return self.send_request('GET', path, query)

    def put(self, path, data=None):
        return self.send_request('PUT', path, data=data)

    def delete(self, path):
        return self.send_request('DELETE', path)

    def get_facts_from(self, listing, primary_field, fields, details_path=None, dynamic_path_indexes=None):
        """Returns facts for the given listing.

        Args:
            details_path (list): List of the path to query to get details.
        """
        ans = []
        search_type = self.module.params['search_type']
        details = self.module.params.get('details')

        for item in listing:
            if self.module.params[primary_field] is not None:
                val = self.module.params[primary_field]
                if search_type == 'exact':
                    if item[primary_field] != val:
                        continue
                elif search_type == 'substring':
                    if val not in item[primary_field]:
                        continue
                elif search_type == 'regex':
                    if not re.search(val, item[primary_field]):
                        continue

            include_item = True
            for field in fields:
                val = self.module.params.get(field)
                if val is not None and item.get(field) != val:
                    include_item = False
                    break

            if include_item:
                if details is None:
                    ans.append(item)
                elif not self.module.params.get('details', False):
                    ans.append(dict((field, item[field]) for field in fields))
                else:
                    path = []
                    for num, p in enumerate(details_path):
                        if num in dynamic_path_indexes:
                            path.append('{0}'.format(item[p]))
                        else:
                            path.append(p)
                    ans.append(self.get(path))

        return {'changed': False, 'listing': ans, 'total': len(ans)}


def search_type_spec():
    return dict(default='exact', choices=['exact', 'substring', 'regex'])


def details_spec():
    return dict(type='bool', default=False)


def state_spec():
    return dict(
        default='present',
        choices=['present', 'absent'],
    )

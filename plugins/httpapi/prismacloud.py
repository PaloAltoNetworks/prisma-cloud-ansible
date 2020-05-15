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

DOCUMENTATION = """
author: Garfield Lee Freeman (@shinmog)
httpapi: prismacloud
short_description: Use prismacloud to interact with Prisma Cloud
description:
    - This prismacloud plugin provides low level access to the Palo
      Alto Networks Prisma Cloud platform.
options:
    customer_name:
        type: str
        description:
            - The customer name
        vars:
            - name: ansible_customer_name
            - name: ansible_httpapi_customer_name
"""

import json

from ansible_collections.paloaltonetworks.prismacloud.plugins.module_utils import errors
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible.module_utils._text import to_text
from ansible.module_utils.connection import Connection
from ansible.module_utils.connection import ConnectionError
from ansible.plugins.httpapi import HttpApiBase


BASE_HEADERS = {
    'Content-Type': 'application/json',
}


class HttpApi(HttpApiBase):
    def send_request(self, method, path, query=None, data=None, headers=None):
        if headers is None:
            headers = BASE_HEADERS

        path = uri(path, query)
        self.connection.queue_message(
            'vvvv',
            '(prismacloud): {0} {1}{2}'.format(method, self.connection._url, path),
        )
        resp, resp_data = self.connection.send(
            path, data=json.dumps(data), method=method, headers=headers,
        )

        code = resp.getcode()
        body = to_text(resp_data.getvalue())

        if code != 200:
            err_loc = 'X-Redlock-Status'
            err_val = resp.get_header(err_loc)
            if err_val is None:
                raise ConnectionError('{0} header is missing, is this Prisma Cloud?\n{1}'.format(err_loc, body))
            errinfo = json.loads(err_val)
            self.connection.queue_message(
                'vvvv',
                '(prismacloud) error: {0}'.format(errinfo),
            )

            # Only ever seen one error at a time, but it's still a list, so....
            for x in errinfo:
                if x['i18nKey'].endswith('_already_exists'):
                    raise errors.AlreadyExistsError("object already exists")
                elif x['i18nKey'] in ('invalid_id', 'not_found'):
                    raise errors.ObjectNotFoundError("object not found")
            else:
                raise errors.PrismaCloudError("error", errinfo)

        ans = None
        try:
            ans = json.loads(body) if body else {}
        except ValueError:
            raise errors.ResponseNotJson("response wasn't json", [body,])

        return ans

    def login(self, username, password):
        path = ['login', ]

        data = {
            'username': username,
            'password': password,
        }
        cn = self.get_option('customer_name')
        if cn is not None:
            data['customerName'] = cn

        ans = self.send_request('POST', path, data=data)
        try:
            self.connection._auth = {'x-redlock-auth': ans['token']}
        except KeyError:
            raise errors.AuthenticationError("invalid authentication credentials")


def uri(path, query=None):
    prefix = '/' + '/'.join('{0}'.format(x) for x in path)

    if query is None:
        return prefix

    suffix = urlencode(query)
    return '{0}?{1}'.format(prefix, suffix)

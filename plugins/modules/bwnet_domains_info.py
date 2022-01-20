#!/usr/bin/python

# Copyright: (c) 2020, Your Name <YourName@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
from ..module_utils import domainctl

DOCUMENTATION = r'''
---
module: bwnet_domains_info

short_description: get a list of domains owned by given user

version_added: "1.0.0"

description: returns a list of DNS domains owned by given user

options:
    username:
        description: name of the user
        required: true
        type: str
    password:
        description: password of the user
        required: true
        type: str
    data:
        description: gather more data about domains
        required: false
        type: bool
        default: false
author:
    - Eric Lavarde (@ericzolf)
'''

EXAMPLES = r'''
# get list of domains
- name: list John Doe's owned domains
  bawunet.domainctl.bwnet_domains_info:
    username: johndoe
    password: secret
  register: __domains_list
'''

RETURN = r'''
domains:
    description: list of DNS domains owned by given user
    type: list
    returned: always
    sample:
        - example.de
        - example.eu
domains_data:
    description: data about the listed domains
    type: list
    returned: optional
    sample: [
            {
                "Dienstname": ".de Domainhosting",
                "Domain-Typ": "Automatischer Standard",
                "Domainname": "example.de",
                "Mailserver": "Spamfilter",
                "Webserver": "virtweb02.bawue.net"
            },
            {
                "Dienstname": ".eu Domainhosting",
                "Domain-Typ": "Automatischer Standard",
                "Domainname": "example.eu",
                "Mailserver": "Spamfilter",
                "Webserver": "virtweb02.bawue.net"
            }
        ]
'''

from ansible.module_utils.basic import AnsibleModule


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        data=dict(type='bool', required=False),
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        domains=[],
        domains_data=[],
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    try:
        result['domains'] = domainctl.get_domains(
                module.params['username'], module.params['password'])
        if module.params['data']:
            headers, data = domainctl.get_domain_data(
                module.params['username'], module.params['password'])
            result['domains_data'] = [dict(zip(headers, x)) for x in data]
    except RuntimeError as exc:
        module.fail_json(exc.args[0])

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()

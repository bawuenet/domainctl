#!/usr/bin/python

# Copyright: (c) 2020, Eric Lavarde <ewl+bawue@lavar.de>
# License: MIT
from __future__ import absolute_import, division, print_function

__metaclass__ = type
from bawuenet.domains import DomainsAPI

DOCUMENTATION = r"""
---
module: bwnet_records_info

short_description: get a list of records for a given domain

version_added: "1.0.0"

description: returns a list of DNS records pertaining to a domain

options:
    username:
        description: name of the user
        required: true
        type: str
    password:
        description: password of the user
        required: true
        type: str
    domain:
        description: name of the domain for which records are to be shown
        required: true
        type: str
author:
    - Eric Lavarde (@ericzolf)
"""

EXAMPLES = r"""
# get list of records
- name: list John Doe's owned records
  bawunet.domainctl.bwnet_records_info:
    username: johndoe
    password: secret
    domain: example.com
  register: __records_list
"""

RETURN = r"""
records:
    description: list of DNS records
    type: list
    returned: always
    sample: [
            {
                "Class": "IN",
                "Owner": "test.example.com",
                "Ressource Record": "192.2.0.1",
                "Type": "A",
                "metadata": {
                    "Domainname": "example.com",
                    "action": "domain-dns-admin-del-zone-entry",
                    "null": "Eintrag löschen",
                    "zoneentryid": "1234"
                }
            }
        ]
"""

from ansible.module_utils.basic import AnsibleModule  # noqa: E402


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        username=dict(type="str", required=True),
        password=dict(type="str", required=True, no_log=True),
        domain=dict(type="str", required=True),
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        records=[],
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    try:
        domainctl = DomainsAPI(module.params["username"], module.params["password"])
        domains = domainctl.get_domains()
        domain = module.params["domain"]
        if domain not in domains:
            module.fail_json(f"Domain {domain} does not belong to user")
        headers, data = domainctl.get_domain_records(domain)
        result["records"] = [dict(zip(headers, x)) for x in data]
    except RuntimeError as exc:
        module.fail_json(exc.args[0])

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()

#!/usr/bin/python

# Copyright: (c) 2020, Eric Lavarde <ewl+bawue@lavar.de>
# License: MIT
from __future__ import absolute_import, division, print_function

__metaclass__ = type
from ..module_utils import domainctl

DOCUMENTATION = r"""
---
module: bwnet_record

short_description: make sure that a DNS record exists (or not) in a domain

version_added: "1.0.0"

description: remove or add a given DNS record from a given domain

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
    host:
        description: short name of the host to add/remove
        required: true
        type: str
    rr:
        description: resource record content
        required: true
        type: str
    type:
        description: type of the record (A, AAAA, NS, TXT, ...)
        required: true
        type: str
    state:
        description: shall the record be present or absent?
        required: false
        type: str
        default: "present"
        choices:
          - present
          - absent
    wait:
        description: wait for the action to have taken effect?
        required: false
        type: bool
        default: false

author:
    - Eric Lavarde (@ericzolf)
"""

EXAMPLES = r"""
# add a record
- name: add John Doe's test server to his domain
  bawunet.domainctl.bwnet_record:
    username: johndoe
    password: secret
    domain: example.com
    host: test
    type: A
    rr: 192.0.2.1
    state: present
    wait: true
"""

RETURN = r"""
"""

from ansible.module_utils.basic import AnsibleModule  # noqa: E402


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        username=dict(type="str", required=True),
        password=dict(type="str", required=True, no_log=True),
        domain=dict(type="str", required=True),
        host=dict(type="str", required=True),
        rr=dict(type="str", required=True),
        type=dict(type="str", required=True),
        state=dict(
            type="str", required=False, default="present", choices=["absent", "present"]
        ),
        wait=dict(type="bool", required=False, default=False),
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    try:
        domains = domainctl.get_domains(
            module.params["username"], module.params["password"]
        )
        domain = module.params["domain"]
        if domain not in domains:
            module.fail_json(f"Domain {domain} does not belong to user")
        if module.params["state"] == "present":
            ret = domainctl.add_record(
                domain,
                module.params["host"],
                module.params["type"],
                module.params["rr"],
                module.params["username"],
                module.params["password"],
            )
        else:
            ret = domainctl.remove_record(
                domain,
                module.params["host"],
                module.params["type"],
                module.params["rr"],
                module.params["username"],
                module.params["password"],
            )
    except RuntimeError as exc:
        module.fail_json(exc.args[0])

    if ret is None:
        # nothing changed
        module.exit_json(**result)
    result["changed"] = True
    if module.params["wait"]:
        if module.params["state"] == "present":
            domainctl.wait_for_add_record(
                domain,
                module.params["host"],
                module.params["type"],
                module.params["rr"],
            )
        else:
            domainctl.wait_for_remove_record(
                domain,
                module.params["host"],
                module.params["type"],
                module.params["rr"],
            )
    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()

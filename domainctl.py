#!/usr/bin/env python3

#
# Simple DNS client for Bawue.Net
#
# Copyright 2020-2023 Andreas Thienemann <andreas@bawue.net>
#
# This code is licensed for use and distribution under the GPLv3+
#

import argparse
from bawuenet.domains import DomainsAPI
import sys

def error(msg):
    sys.stderr.write("ERROR:   " + msg + "\n")

def warn(msg):
    sys.stderr.write("WARNING: " + msg + "\n")


def print_domains(output, client):
    """Pretty print a table of domains owned"""
    headers, data = client.get_domain_data()
    print(output(data, headers=headers))


def print_domain_records(domain, output, client):
    """Pretty print a table of domain contents"""
    headers, data = client.get_domain_records(domain)
    print(output([x[:-1] for x in data], headers=headers[:-1]))


def output_table(data, headers):
    import tabulate

    return tabulate.tabulate(data, headers=headers)


def output_json(data, headers):
    import json

    return json.dumps([dict(zip(headers, x)) for x in data], indent=2)


def output_yaml(data, headers):
    import yaml

    return yaml.dump([dict(zip(headers, x)) for x in data], indent=2)


def main():
    description = """Bawue.Net DNS client

Erlaubt via dem MyBawue.Net Webinterface einfach einen DNS Eintrag
hinzuzufügen oder zu entfernen"""

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "action",
        type=str,
        help="one possible DNS action",
        choices=["list_domains", "list_records", "add_record", "remove_record"],
    )
    parser.add_argument("--username", type=str, help="username", required=True)
    parser.add_argument("--password", type=str, help="password", required=True)
    parser.add_argument("--host", type=str, help="host name (without domain)")
    parser.add_argument("--domain", type=str, help="domain")
    parser.add_argument("--type", type=str, help="type")
    parser.add_argument("--rr", type=str, help="rr")
    parser.add_argument("--wait", action="store_true", help="wait")
    parser.add_argument(
        "--format",
        type=str,
        help="output format",
        choices=["table", "yaml", "json"],
        default="table",
    )

    # Parse arguments
    args = parser.parse_args()
    # choose the right output format function
    output = globals()["output_" + args.format]

    domain_api = DomainsAPI(args.username, args.password)

    # execute the selected action
    if args.action == "list_domains":
        print_domains(output, domain_api)
    elif args.action == "list_records":
        if not args.domain:
            error("--domain muss definiert sein")
            sys.exit(1)
        if args.domain not in domain_api.get_domains():
            error("%s gehört dem Nutzer nicht" % args.domain)
            sys.exit(2)
        print_domain_records(args.domain, output, domain_api)
    elif args.action == "add_record" or args.action == "remove_record":
        for var in ("domain", "host", "type", "rr"):
            if not getattr(args, var):
                error("--%s muss definiert sein" % var)
                sys.exit(1)
        if args.domain not in domain_api.get_domains():
            error("%s gehört dem Nutzer nicht" % args.domain)
            sys.exit(2)
        # call the action function by its name
        ret = getattr(domain_api, args.action)(
            args.domain, args.host, args.type, args.rr
        )
        if ret is None:  # nothing modified
            sys.exit(-1)
        if args.wait:
            print(
                "Waiting for DNS change...",
            )
            getattr(domain_api, "wait_for_" + args.action)(
                args.domain, args.host, args.type, args.rr
            )


if __name__ == "__main__":
    main()

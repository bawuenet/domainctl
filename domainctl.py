#!/usr/bin/env python3

#
# Simple DNS client for Bawue.Net
#
# Copyright 2020 Andreas Thienemann <andreas@bawue.net>
#
# This code is licensed for use and distribution under the GPLv3+
#

import argparse
import requests
import socket
import sys
import time
from dns.resolver import NXDOMAIN, Resolver
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth

base_url = "https://my.bawue.net/domains.php"
auth_ns = "ns1.bawue.net"
username = None
password = None

type_table = {
    "A": 1,
    "CNAME": 2,
    "MX": 4,
    "TXT": 8,
    "AAAA": 128,
    "NS": 256,
    "SRV": 512,
}


def error(msg):
    sys.stderr.write("ERROR:   " + msg + "\n")


def warn(msg):
    sys.stderr.write("WARNING: " + msg + "\n")


def parse_html_table(table, formdata=False):
    """Parse a html table, return headers and data"""
    headers = [x.text for x in table.find("tr").find_all("th")]
    data = []
    metadata = []
    for row in table.find_all("tr")[1:]:
        if formdata and row.find("form"):
            metadata.append(
                dict(
                    [
                        (input.get("name"), input.get("value"))
                        for input in row.find("form").find_all("input")
                    ]
                )
            )
        else:
            metadata.append({})
        data.append([x.text.strip() for x in row.find_all("td") if len(x.text) > 0])
    if formdata:
        return ([x for x in headers if len(x) > 0], data, metadata)
    else:
        return ([x for x in headers if len(x) > 0], data)


def get_domain_data():
    """Get user owned domains"""
    r = requests.get("%s" % base_url, auth=HTTPBasicAuth(username, password))
    if r.status_code != 200:
        raise RuntimeError("Not authorized")
    soup = BeautifulSoup(r.text, "html.parser")
    data = soup.find("table")
    headers, data = parse_html_table(data)
    return (headers[:-1], [x[:-1] for x in data])


def get_domains():
    """Get a list of domains"""
    return sorted([x[0] for x in get_domain_data()[1]])


def print_domains(output):
    """Pretty print a table of domains owned"""
    headers, data = get_domain_data()
    print(output(data, headers=headers))


def get_domain_records(domain):
    """Get RRs from a domain"""
    params = {"domain": domain, "action": "edit"}
    r = requests.get(
        "%s" % base_url, auth=HTTPBasicAuth(username, password), params=params
    )
    if r.status_code != 200:
        raise RuntimeError("Not authorized")
    soup = BeautifulSoup(r.text, "html.parser")
    data = soup.find("table")
    headers, data, metadata = parse_html_table(data, True)
    table = []
    for idx in range(len(data)):
        table.append(data[idx] + [metadata[idx]])
    return (headers + ["metadata"], table)


def print_domain_records(domain, output):
    """Pretty print a table of domain contents"""
    headers, data = get_domain_records(domain)
    print(output([x[:-1] for x in data], headers=headers[:-1]))


def add_record(domain, host, dnstype, rr):
    """Add a record to the DNS"""
    fullhost = host + "." + domain
    headers, records = get_domain_records(domain)
    # keep only the records fitting our criteria
    records = [
        y
        for y in [dict(zip(headers, x)) for x in records]
        if y["Owner"] == fullhost and y["Ressource Record"] == rr
    ]
    if records:
        warn(f"Record {fullhost} with ressource {rr} already exists")
        return None  # nothing to be done
    params = {
        "owner": host,
        "type": type_table[dnstype],
        "RRecord": rr,
        "Domainname": domain,
        "action": "domain-dns-admin-commit-zone-entry",
    }
    r = requests.get(
        "%s" % base_url, auth=HTTPBasicAuth(username, password), params=params
    )
    if r.status_code != 200:
        error(f"Not authorized to add {host} to {domain} due to {r}")
        return False
    else:
        return True


def remove_record(domain, host, dnstype, rr):
    """Remove a record from the DNS"""
    fullhost = host + "." + domain
    headers, records = get_domain_records(domain)
    # keep only the records fitting our criteria
    records = [
        y
        for y in [dict(zip(headers, x)) for x in records]
        if y["Owner"] == fullhost and y["Ressource Record"] == rr
    ]
    if not records:
        warn(f"Record {fullhost} with ressource {rr} not found")
        return None  # nothing to be done
    for r in records:
        rr_id = r["metadata"]["zoneentryid"]
        params = {
            "Domainname": domain,
            "zoneentryid": rr_id,
            "action": "domain-dns-admin-del-zone-entry",
        }
        r = requests.get(
            "%s" % base_url, auth=HTTPBasicAuth(username, password), params=params
        )
        if r.status_code != 200:
            error(f"Not authorized to remove {host} from {domain} due to {r}")
            return False
        # we don't leave the loop so that all records with the same
        # combination are removed
    return True


def query_dns_server(record, type):
    resolver = Resolver(configure=False)
    resolver.nameservers = [socket.gethostbyname(auth_ns)]
    resolver.timeout = 5
    resolver.lifetime = 5
    try:
        dns_query = resolver.resolve(record, type)
        return dns_query
    except NXDOMAIN:
        return False


def wait_for_record_add(domain, host, type, rr):
    print(
        "Waiting for DNS change...",
    )
    for i in range(22):
        answer = query_dns_server("%s.%s." % (host, domain), type)
        try:
            for i in answer.response.answer:
                for j in i.items:
                    if rr in j.to_text():
                        return
        except (AttributeError, TypeError):
            pass
        time.sleep(30)
        print(
            ".",
        )
    raise RuntimeError("Timeout exceeded waiting for DNS change...")


def wait_for_record_remove(domain, host, type, rr):
    print(
        "Waiting for DNS change...",
    )
    for i in range(22):
        if not query_dns_server("%s.%s." % (host, domain), type):
            return
        time.sleep(30)
        print(
            ".",
        )
    raise RuntimeError("Timeout exceeded waiting for DNS change...")


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

    global username
    global password
    username = args.username
    password = args.password

    # choose the right output format function
    output = globals()["output_" + args.format]

    # execute the selected action
    if args.action == "list_domains":
        print_domains(output)
    elif args.action == "list_records":
        if not args.domain:
            error("--domain muss definiert sein")
            sys.exit(1)
        if args.domain not in get_domains():
            error("%s gehört dem Nutzer nicht" % args.domain)
            sys.exit(2)
        print_domain_records(args.domain, output)
    elif args.action == "add_record" or args.action == "remove_record":
        for var in ("domain", "host", "type", "rr"):
            if not getattr(args, var):
                error("--%s muss definiert sein" % var)
                sys.exit(1)
        if args.domain not in get_domains():
            error("%s gehört dem Nutzer nicht" % args.domain)
            sys.exit(2)
        # call the action function by its name
        ret = globals()[args.action](args.domain, args.host, args.type, args.rr)
        if ret:  # action was successful
            if args.wait:
                wait_for_record_add(args.domain, args.host, args.type, args.rr)
        elif ret is None:
            sys.exit(-1)  # nothing modified
        else:  # error
            sys.exit(3)


if __name__ == "__main__":
    main()

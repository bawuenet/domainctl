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
import sys
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from tabulate import tabulate
from pprint import pprint

base_url = "https://my.bawue.net/domains.php"
username = None
password = None

type_table = {'A': 1,
              'CNAME': 2,
              'MX': 4,
              'TXT': 8,
              'AAAA': 128,
              'NS': 256,
              'SRV': 512,
             }

def parse_html_table(table, formdata=False):
    """ Parse a html table, return headers and data """
    headers = [x.text for x in table.find('tr').find_all('th')]
    data = []
    metadata = []
    for row in table.find_all('tr')[1:]:
        if formdata and row.find('form'):
            metadata.append(dict([(input.get('name'), input.get('value')) for input in row.find('form').find_all('input')]))
        else:
            metadata.append({})
        data.append([x.text for x in row.find_all('td') if len(x.text) > 0])
    if formdata:
        return ([x for x in headers if len(x) > 0], data, metadata)
    else:
        return ([x for x in headers if len(x) > 0], data)

def get_domain_data():
    """ Get user owned domains """
    r = requests.get('%s' % base_url, auth=HTTPBasicAuth(username, password))
    if r.status_code != 200:
        raise RuntimeError("Not authorized")
    soup = BeautifulSoup(r.text, 'html.parser')
    data = soup.find('table')
    headers, data = parse_html_table(data)
    return (headers[:-1], [x[:-1] for x in data])

def get_domains():
    """ Get a list of domains """
    return sorted([x[0] for x in get_domain_data()[1]])

def print_domains():
    """ Pretty print a table of domains owned """
    headers, data = get_domain_data()
    print(tabulate(data, headers=headers))

def get_domain_records(domain):
    """ Get RRs from a domain """
    params = {'domain': domain, 'action': 'edit'}
    r = requests.get('%s' % base_url, auth=HTTPBasicAuth(username, password), params=params)
    if r.status_code != 200:
        raise RuntimeError("Not authorized")
    soup = BeautifulSoup(r.text, 'html.parser')
    data = soup.find('table')
    headers, data, metadata = parse_html_table(data, True)
    table = []
    for idx in range(len(data)):
        table.append(data[idx] + [metadata[idx]])
    return (headers + ['metadata'], table)

def print_domain_records(domain):
    """ Pretty print a table of domain contents """
    headers, data = get_domain_records(domain)
    print(tabulate([x[:-1] for x in data], headers=headers[:-1]))

def add_record(domain, host, type, rr):
    """ Add a record to the DNS """
    params = {'owner': host, 'type': type_table[type], 'RRecord': rr, 'Domainname': domain, 'action': 'domain-dns-admin-commit-zone-entry' }
    r = requests.get('%s' % base_url, auth=HTTPBasicAuth(username, password), params=params)
    if r.status_code != 200:
        raise RuntimeError("Not authorized")


def remove_record(domain, host, type, rr):
    """ Remove a record from the DNS """
    headers, records = get_domain_records(domain)
    for r in records:
        r = dict(zip(headers, r))
        if '%s.%s' % (host, domain) == r['Owner'] and rr == r['Ressource Record']:
            rr_id = r['metadata']['zoneentryid']
    params = {'Domainname': domain, 'zoneentryid': rr_id, 'action': 'domain-dns-admin-del-zone-entry' }
    r = requests.get('%s' % base_url, auth=HTTPBasicAuth(username, password), params=params)
    if r.status_code != 200:
        raise RuntimeError("Not authorized")

def main():
    description = """Bawue.Net DNS client

Erlaubt via dem MyBawue.Net Webinterface einfach einen DNS Eintrag hinzuzufügen oder zu entfernen"""

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("action", type=str, help="")
    parser.add_argument("--username", type=str, help="username", required=True)
    parser.add_argument("--password", type=str, help="password", required=True)
    parser.add_argument("--host", type=str, help="host")
    parser.add_argument("--domain", type=str, help="domain")
    parser.add_argument("--type", type=str, help="type")
    parser.add_argument("--rr", type=str, help="rr")

    # Parse arguments
    args = parser.parse_args()

    global username
    global password
    username = args.username
    password = args.password

    if args.action == 'list_domains':
        print_domains()
    if args.action == 'list_records':
        if not args.domain:
            print("--domain muss definiert sein")
            sys.exit(1)
        if args.domain not in get_domains():
            print("%s gehört dem Nutzer nicht" % args.domain)
            sys.exit(2)
        print_domain_records(args.domain)
    if args.action == 'add_record':
        for var in ('domain', 'host', 'type', 'rr'):
            if not getattr(args, var):
                print("--%s muss definiert sein" % var)
                sys.exit(1)
        if args.domain not in get_domains():
            print("%s gehört dem Nutzer nicht" % args.domain)
            sys.exit(2)
        add_record(args.domain, args.host, args.type, args.rr)
    if args.action == 'remove_record':
        for var in ('domain', 'host', 'type', 'rr'):
            if not getattr(args, var):
                print("--%s muss definiert sein" % var)
                sys.exit(1)
        if args.domain not in get_domains():
            print("%s gehört dem Nutzer nicht" % args.domain)
            sys.exit(2)
        remove_record(args.domain, args.host, args.type, args.rr)

if __name__ == "__main__":
    main()

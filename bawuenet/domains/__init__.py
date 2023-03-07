#!/usr/bin/env python3
#
# Simple DNS client for Bawue.Net
#
# Copyright 2023 Andreas Thienemann <andreas@bawue.net>
#
# This code is licensed for use and distribution under the GPLv3+
#

import requests
import socket
import time
import sys
from dns.resolver import NXDOMAIN, Resolver, LifetimeTimeout
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth

def error(msg):
    sys.stderr.write("ERROR:   " + msg + "\n")

def warn(msg):
    sys.stderr.write("WARNING: " + msg + "\n")

class DomainsAPI:
    base_url = "https://my.bawue.net/domains.php"
    auth_ns = "ns1.bawue.net"

    type_table = {
        "A": 1,
        "CNAME": 2,
        "MX": 4,
        "TXT": 8,
        "AAAA": 128,
        "NS": 256,
        "SRV": 512,
    }

    def __init__(self, username, password):
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(username, password)

    def parse_html_table(self, table, formdata=False):
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

    def get_domain_data(self):
        """Get user owned domains"""
        r = self.session.get("%s" % self.base_url)
        if not r.ok:
            raise RuntimeError(f"Request failed due to {r.reason} ({r.status_code})")
        soup = BeautifulSoup(r.text, "html.parser")
        data = soup.find("table")
        headers, data = self.parse_html_table(data)
        return (headers[:-1], [x[:-1] for x in data])

    def get_domains(self):
        """Get a list of domains"""
        return sorted([x[0] for x in self.get_domain_data()[1]])

    def get_domain_records(self, domain):
        """Get RRs from a domain"""
        params = {"domain": domain, "action": "edit"}
        r = self.session.get("%s" % self.base_url, params=params)
        if not r.ok:
            raise RuntimeError(f"Request failed due to {r.reason} ({r.status_code})")
        soup = BeautifulSoup(r.text, "html.parser")
        data = soup.find("table")
        headers, data, metadata = self.parse_html_table(data, True)
        table = []
        for idx in range(len(data)):
            table.append(data[idx] + [metadata[idx]])
        return (headers + ["metadata"], table)

    def add_record(self, domain, host, dnstype, rr):
        """Add a record to the DNS"""
        fullhost = host + "." + domain
        headers, records = self.get_domain_records(domain)
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
            "type": self.type_table[dnstype],
            "RRecord": rr,
            "Domainname": domain,
            "action": "domain-dns-admin-commit-zone-entry",
        }
        r = self.session.get("%s" % self.base_url, params=params)
        if r.status_code != 200:
            raise RuntimeError(f"Request failed due to {r.reason} ({r.status_code})")
        else:
            return True

    def remove_record(self, domain, host, dnstype, rr):
        """Remove a record from the DNS"""
        fullhost = host + "." + domain
        headers, records = self.get_domain_records(domain)
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
            r = self.session.get("%s" % self.base_url, params=params)
            if r.status_code != 200:
                raise RuntimeError(
                    f"Request failed due to {r.reason} ({r.status_code})"
                )
            # we don't leave the loop so that all records with the same
            # combination are removed
        return True

    def query_dns_server(self, record, type):
        resolver = Resolver(configure=False)
        resolver.nameservers = [socket.gethostbyname(auth_ns)]
        resolver.timeout = 5
        resolver.lifetime = 5
        try:
            dns_query = resolver.resolve(record, type)
            return dns_query
        except (NXDOMAIN, LifetimeTimeout):
            return False

    def wait_for_add_record(self, domain, host, type, rr):
        for i in range(22):
            answer = self.query_dns_server("%s.%s." % (host, domain), type)
            try:
                for i in answer.response.answer:
                    for j in i.items:
                        if rr in j.to_text():
                            sys.stdout.write("\n")
                            sys.stdout.flush()
                            return
            except (AttributeError, TypeError):
                pass
            time.sleep(30)
            sys.stdout.write(".")
            sys.stdout.flush()
        raise RuntimeError("Timeout exceeded waiting for DNS change...")

    def wait_for_remove_record(self, domain, host, type, rr):
        for i in range(22):
            if not self.query_dns_server("%s.%s." % (host, domain), type):
                sys.stdout.write("\n")
                sys.stdout.flush()
                return
            time.sleep(30)
            sys.stdout.write(".")
            sys.stdout.flush()
        raise RuntimeError("Timeout exceeded waiting for DNS change...")

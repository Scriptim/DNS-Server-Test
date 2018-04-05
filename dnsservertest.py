#!/bin/python3

import dns.resolver
import json
import os.path
import time

directory = os.path.dirname(__file__)

with open(os.path.join(directory, "servers.json"), encoding="utf-8-sig") as servers_file:
    servers = json.load(servers_file)
with open(os.path.join(directory, "domains.txt"), encoding="utf-8-sig") as servers_file:
    domains = servers_file.read().splitlines()


def test_server(server, alternate=False):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [server["preferred"] if not alternate else server["alternate"]]
    resolver.timeout = resolver.lifetime = 1

    minimum = float("inf")
    average = 0
    maximum = 0
    timeouts = 0

    for domain in domains:
        start = time.time()
        try:
            query = resolver.query(domain)
        except dns.exception.Timeout as timeout:
            timeouts = timeouts + 1
            if timeouts >= len(domains) / 2:
                # cancel on 50% timeouts
                return None
            continue
        duration = time.time() - start

        minimum = min(duration, minimum)
        average = average + duration
        maximum = max(duration, maximum)

    average = average / (len(domains) - timeouts)

    return (minimum, average, maximum, timeouts)


for server in servers:
    print(server)
    results_pref = test_server(server)
    print(results_pref)
    if "alternate" in server:
        print(str(server) + " (alternate)")
        results_alt = test_server(server, True)
        print(results_alt)

#!/bin/python3

import dns.resolver
import json
import os.path
import signal
import sys
import termcolor
import time


def exit_on_sigint(a, b):
    print()
    print(termcolor.colored("Interrupted", "red", attrs=["bold"]))
    sys.exit(137)


signal.signal(signal.SIGINT, exit_on_sigint)

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
        except Exception as exception:
            return None
        duration = time.time() - start

        minimum = min(duration, minimum)
        average = average + duration
        maximum = max(duration, maximum)

    average = average / (len(domains) - timeouts)

    return (minimum, average, maximum, timeouts)


def print_results(results):
    if results != None:
        print(termcolor.colored("min:"), end=" ")
        print(termcolor.colored(round(results[0], 5), attrs=["bold"]), end="ms | ")
        print(termcolor.colored("avg:"), end=" ")
        print(termcolor.colored(round(results[1], 5), attrs=["bold", "underline"]), end="ms | ")
        print(termcolor.colored("max:"), end=" ")
        print(termcolor.colored(round(results[2], 5), attrs=["bold"]), end="ms ")
        percentage_timeouts = round(results[3] / len(domains) * 100)
        if percentage_timeouts == 0:
            print(termcolor.colored("(" + str(percentage_timeouts) + "% timeouts)", "green", attrs=["dark"]))
        elif percentage_timeouts < 10:
            print(termcolor.colored("(" + str(percentage_timeouts) + "% timeouts)", "yellow", attrs=["dark"]))
        else:
            print(termcolor.colored("(" + str(percentage_timeouts) + "% timeouts)", "red", attrs=["dark"]))
    else:
        print(termcolor.colored("Too many timeouts or an exception occured", "red"))


def server_score(results):
    if results != None:
        minimum = results[0]
        average = results[1]
        maximum = results[2]
        timeouts = results[3]

        return 4 * (1 / average - timeouts) + 1 / minimum - 1 / maximum
    else:
        return -100


server_results = []

for server in servers:
    print(termcolor.colored(server["name"], "blue", attrs=["bold"]))
    print(termcolor.colored("  " + server["preferred"], "cyan"), end="  ")
    results_pref = test_server(server)
    server_results.append((server["name"], server["preferred"], server_score(results_pref), False))
    print_results(results_pref)
    if "alternate" in server:
        print(termcolor.colored("  " + server["alternate"], "cyan"), end=" ")
        print(termcolor.colored("(alt)", "cyan", attrs=["dark"]), end="  ")
        results_alt = test_server(server, True)
        server_results.append((server["name"], server["alternate"], server_score(results_alt), True))
        print_results(results_alt)

server_results = sorted(server_results, key=lambda server: server[2], reverse=True)
print()
print(termcolor.colored("====[ RECOMMENDATIONS ]====", "blue", attrs=["bold"]))
for i in range(5):
    result = server_results[i]
    print(termcolor.colored(i + 1, "blue", attrs=["bold"]), end=" ")
    print(termcolor.colored(result[0], "blue"), end=" ")
    if result[3]:
        print(termcolor.colored("(alt)", "blue", attrs=["dark"]), end=" ")
    print(termcolor.colored(result[1], "cyan"))

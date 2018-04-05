#!/bin/python3

import json
import os.path

directory = os.path.dirname(__file__)

with open(os.path.join(directory, "servers.json"), encoding="utf-8-sig") as servers_file:
    servers = json.load(servers_file)
with open(os.path.join(directory, "domains.txt"), encoding="utf-8-sig") as servers_file:
    domains = servers_file.read().splitlines()

# DNS Server Test

Automatically test the performance of a bunch of DNS servers to find the best one

## Requirements

This program requires Python 3

To install the required packages run `pip3 install -r requirements.txt`

## `servers.json` and `domains.txt`

`servers.json` contains 21 public DNS servers in JSON format, feel free to expand it (note that the `alternate` attribute is optional)

`domains.txt` contains a list of domains of the 30 most popular websites (according to [Wikipedia](https://en.wikipedia.org/wiki/List_of_most_popular_websites "Wikipedia: List of most popular websites")) that are used to test the performance

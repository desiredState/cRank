# cRank

cRank accepts a query string (e.g. a YouTube video topic) and a matcher (e.g. a specific YouTube channel) then cycles through a complete list of iso3166 countries, attempting to connect to a TOR node from each, and generates a ranking report based on the country, the query string and the search ranking of the matcher. The typical use-case of cRank is to determine if a matcher is being politically censored within a given country by comparing its global search ranking results.

### Usage

```bash
usage: crank.py [-h] [-d] [-s SOCKS_PROXY] [-o SOCKS_PORT] -p {youtube} -q QUERY -m MATCHER

arguments:
  -h, --help      show this help message and exit
  -d, --debug
  -s SOCKS_PROXY, --socks-proxy SOCKS_PROXY
  -o SOCKS_PORT,  --socks-port SOCKS_PORT
  -p {youtube},   --platform {youtube}
  -q QUERY,       --query QUERY
  -m MATCHER,     --matcher MATCHER
```

E.g.

```bash
./crank.py -d -p youtube -q 'google election meddling' -m 'https://www.youtube.com/user/StevenCrowder'
```

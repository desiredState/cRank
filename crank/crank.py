#!/usr/bin/env python3

import argparse
import logging
import sys
from pprint import pformat
from urllib.parse import urlencode

import numpy
from iso3166 import countries
from matplotlib import pyplot
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from stem import process as tor


class CRank(object):
    """
        cRank accepts a query string (e.g. a YouTube video topic) and a matcher (e.g. a specific YouTube channel)
        then cycles through a complete list of iso3166 countries, attempting to connect to a TOR node from each, and
        generates a ranking report based on the country, the query string and the search ranking of the matcher.
        The typical use-case of cRank is to determine if a matcher is being politically censored within a given country
        by comparing its global search ranking results.
    """

    def __init__(self, debug=False):
        """
        Args:
            :param debug (bool): Use the debug logging level.
        """

        logging.basicConfig(format='%(message)s', level=logging.INFO)
        self.logger = logging.getLogger('crank')

        if debug:
            self.logger.setLevel(logging.DEBUG)

    def run(self, platform, query, matcher, socks_proxy='127.0.0.1', socks_port=7321):
        """ Execute the cRank report.
        Args:
            :param platform (str): The platform to query (e.g. "youtube").
            :param query (str): A query string (e.g. a YouTube video title).
            :param matcher (str): A matcher (e.g. a specific YouTube video URL).
            :param socks_proxy (str): The TOR SOCKS proxy address.
            :param socks_port (int): The TOR SOCKS proxy port.
        """

        self.logger.debug(f'Using platform: {platform}')
        self.logger.debug(f'Using query: {query}')
        self.logger.debug(f'Using matcher: {matcher}')
        self.logger.debug(f'Using SOCKS proxy: {socks_proxy}:{socks_port}')

        headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 '
                                 '(KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}

        results = {}

        for country in countries:
            self.logger.info(f'Querying via {country[0]} ({country[1]})...')

            try:
                tor_process = tor.launch_tor_with_config(
                    timeout=10,
                    take_ownership=True,
                    config={
                        'SOCKSPort': str(socks_port),
                        'ExitNodes': f'{{{country[1]}}}',
                        'StrictNodes': '1',

                    }
                )

                if platform == 'youtube':
                    rank = self.get_youtube_rank(
                        proxy=f'socks5://{socks_proxy}:{socks_port}',
                        headers=headers,
                        matcher=matcher,
                        query=query
                    )

                results[country[0]] = rank

            except OSError:
                self.logger.exception(f'No TOR node found in {country[1]}, skipping...')
                continue

            except Exception as e:
                self.logger.exception(f'Failed to query with exception: {e}')
                sys.exit(1)

            finally:
                try:
                    tor_process.kill()
                except Exception:
                    pass

        self.logger.debug(f'Results:\n{pformat(results)}')
        self.generate_graph(results)

    def get_youtube_rank(self, proxy, headers, matcher, query):
        """ Return the YouTube search rank of a matcher given a search query.
        Args:
            :param session:
            :param headers:
            :param matcher:
            :param query:
        Return:
            :return:
        """

        search_url = f'https://www.youtube.com/results?{urlencode({"search_query": query})}'
        self.logger.debug(f'Encoded search URL: {search_url}')

        options = Options()
        options.add_argument("--headless")
        options.add_argument(f'user-agent={headers}')
        options.add_argument(f'--proxy-server={proxy}')

        driver = webdriver.Chrome(options=options)
        driver.get(search_url)

        videos = driver.find_elements_by_id('dismissable')

        channel_urls = []
        for video in videos:
            c1 = video.find_element_by_id('channel-name')
            c2 = c1.find_element_by_class_name('yt-simple-endpoint')

            channel_urls.append(c2.get_attribute('href'))

        driver.close()

        try:
            rank = channel_urls.index(matcher) + 1
        except ValueError:
            rank = 0

        self.logger.debug(f'Rank: {rank}')

        return rank

    def generate_graph(self, results):
        """ Generate and display a graph of cRank results.
        Args:
            :param results (dict): cRank results.
        """

        y_pos = numpy.arange(len(results.keys()))

        pyplot.bar(y_pos, results.values())
        pyplot.xticks(y_pos, results.keys(), rotation=90)
        pyplot.subplots_adjust(bottom=0.4, top=0.99)

        pyplot.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', default=False)
    parser.add_argument('-s', '--socks-proxy', type=str, default='127.0.0.1')
    parser.add_argument('-o', '--socks-port', type=int, default=7321)
    parser.add_argument('-p', '--platform', type=str, required=True, choices=['youtube'])
    parser.add_argument('-q', '--query', type=str, required=True)
    parser.add_argument('-m', '--matcher', type=str, required=True)
    args = parser.parse_args()

    crank = CRank(debug=args.debug)
    crank.run(
        platform=args.platform,
        query=args.query,
        matcher=args.matcher,
        socks_proxy=args.socks_proxy,
        socks_port=args.socks_port
    )

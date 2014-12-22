""" RoboCop 2 LinkParse.py - A parsing agent and library"""

import re
from bs4 import BeautifulSoup
import requests
from cloudbot.util import formatting

headers_mac = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.'}
headers_win = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36'}
headers_lin = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36'}
headers_bot = {'User-Agent': 'RoboCop/2.0 (KHTML, like Gecko) - RoboCop by Foxlet'}


def parse(link, agent):
    if agent == "mac":
        headers = headers_mac
    elif agent == "win":
        headers = headers_win
    elif agent == "lin":
        headers = headers_lin
    else:
        headers = headers_bot
    try:
        data = requests.get(link, headers=headers)
    except requests.exceptions.MissingSchema:
        raise FormatError('Invalid or malformed link.')
    page = data.text
    soup = BeautifulSoup(page)

    if soup is None:
        raise FormatError('Unrecognized format or non-HTML link.')

    return soup

class meta:
    'linkparse.meta - Parses an HTTP link and returns with relevant metadata.'
    def __init__(self, link, agent):
        self.l = link
        self.a = agent
        try:
            self.data = parse(self.l, self.a)
        except:
            raise FormatError('Unrecognized format or non-HTML link.')

    def title(self):
        data = self.data
        try:
            title_clean = re.sub('\s+',' ', data.title.string)
        except AttributeError:
            raise FormatError('Link has no title.')
        return title_clean

    def description(self):
        data = self.data
        description_clean = ""
        meta1 = data.find_all('meta',attrs={'name':'Description'})
        meta2 = data.find_all('meta',attrs={'name':'description'})

        for tag in meta1:
            description_clean += str(tag['content'])
        for tag in meta2:
            description_clean += str(tag['content'])

        description_clean = formatting.truncate_str(description_clean, 136)

        return description_clean

class FormatError(Exception):
    def __init__(self, info):
        self.info = info
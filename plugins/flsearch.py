from cloudbot import hook
from cloudbot.util import linkparse
import requests

@hook.command
def feelinglucky(text):
    remote = 'https://www.google.com/search?q={}&btnI=1'.format(text)
    response = requests.get(remote)
    tags = linkparse.meta (response.url, agent='lin')
    return u'{} -- \x02{}\x02: "{}"'.format(response.url, tags.title(), tags.description())
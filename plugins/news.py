# RoboCop 2's news.py, picks a random article from Google News.

from cloudbot import hook
import feedparser
import random

@hook.command(autohelp=False)
def news(text):
	"""news - prints a random headline from Google News"""
	d = feedparser.parse('https://news.google.com/news/feeds?pz=1&cf=all&ned=us&hl=en&output=rss')
	counter = len(d['entries'])
	counter = counter - 1
	value = random.randint(0, counter)
	returnitem = d.entries[value]['title'] 
	return str(returnitem)

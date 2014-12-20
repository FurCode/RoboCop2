import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
from cloudbot import hook
import random
import base64
import requests
import json
import datetime
import imghdr
import urllib
import os
import textwrap

@hook.command
def meme(text):
	#import sys

	args = text

	if ";" in args:
		arguments = args.split(";")
		count = len(arguments)
		if count == 2:
			# args give meme and one line
			topString = ''
			bottomString = arguments[1]
			#bottomString = textwrap.fill(bottomString, width=40)
			meme = arguments[0]
		elif count == 3:
			# args give meme and two lines
			topString = arguments[1]
			#topString = textwrap.fill(topString, width=40)
			bottomString = arguments[2]
			#bottomString = textwrap.fill(bottomString, width=40)
			meme = arguments[0]
		else:
			# so many args
			# what do they mean
			# too intense
			return 'Too many args...'
	else:
			# only one argument, use standard meme
			topString = ''
			bottomString = args
			meme = 'standard'

	

	print(meme);

	img = Image.open('plugins/memes/'+str(meme)+'.jpg')
	imageSize = img.size

	# find biggest font size that works
	fontSize = imageSize[1]//5
	font = ImageFont.truetype("plugins/Impact.ttf", fontSize)
	topTextSize = font.getsize(topString)
	bottomTextSize = font.getsize(bottomString)
	while topTextSize[0] > imageSize[0]-20 or bottomTextSize[0] > imageSize[0]-20:
		fontSize = fontSize - 1
		font = ImageFont.truetype("plugins/Impact.ttf", fontSize)
		topTextSize = font.getsize(topString)
		bottomTextSize = font.getsize(bottomString)

	# find top centered position for top text
	topTextPositionX = (imageSize[0]//2) - (topTextSize[0]//2)
	topTextPositionY = 0
	topTextPosition = (topTextPositionX, topTextPositionY)

	# find bottom centered position for bottom text
	bottomTextPositionX = (imageSize[0]//2) - (bottomTextSize[0]//2)
	factor = bottomTextSize[1] * 0.5
	add = bottomTextSize[1] + factor
	bottomTextPositionY = imageSize[1] - add
	bottomTextPosition = (bottomTextPositionX, bottomTextPositionY)

	draw = ImageDraw.Draw(img)

	# draw outlines
	# there may be a better way
	outlineRange = fontSize//15
	for x in range(-outlineRange, outlineRange+1):
		for y in range(-outlineRange, outlineRange+1):
			draw.text((topTextPosition[0]+x, topTextPosition[1]+y), topString, (0,0,0), font=font)
			draw.text((bottomTextPosition[0]+x, bottomTextPosition[1]+y), bottomString, (0,0,0), font=font)

	draw.text(topTextPosition, topString, (255,255,255), font=font)
	draw.text(bottomTextPosition, bottomString, (255,255,255), font=font)

	img.save("temp.png")
	imgtpath = ""
	API_KEY = "1ae994097d741ae"
	filename = "temp.png"
	#image_path = os.path.join(imgtpath,filename)
	image_path = "temp.png"
	#urllib.urlretrieve(inp, image_path)

	#b = requests.get(inp)
	#with open(image_path, "wb") as code:
	#	code.write(b.content)

	headers = {'Authorization': 'Client-ID ' + API_KEY}
	format = imghdr.what(image_path)
	print(format);
	image_path_fixed = image_path
	fh = open(image_path_fixed, 'rb');
	base64img = base64.b64encode(fh.read())
	url="https://api.imgur.com/3/upload.json"
	r = requests.post(url, data={'key': API_KEY, 'image':base64img,'title':'meme'},headers=headers,verify=False)
	print(r.text);
	val=json.loads(r.text)
	try:
		return val['data']['link']
	except KeyError:
		return val['data']['error']

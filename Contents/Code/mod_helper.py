#!/usr/bin/python
import re
debug = True

def getMediaLinkConfig(string):
	config = { 'media': '',
		'vcodec': '',
		'acodec': '',
		'container': ''
	}
	m = re.search('\$plex\[(.*)\]', string)

	try:
		configvalues = m.group(1).split(',')

		# Get configvalues from configstring.
		for value in configvalues:
			# Check media.
			if value == "movie" or value == "tvseries" or value == "clip":
				config['media'] = value

			# Check videocodec.
			if value == "h264":
				config['vcodec'] = value

			# Check audiocodec.
			if value == "aac" or value == "mp3" or value == "ac3":
				config['acodec'] = value

			# Check container.
			if value == "mp4" or value == "mkv" or value == "mov" or value == "avi":
				config['container'] = value
	except:
		if debug == True: Log("No valid valid configuration found for media.")
		return False
	return config

def hasPlexMovieTag(string):
	tmp = getMediaLinkConfig(string)

	if tmp != False:
		if tmp['media'] == "movie":
			return True
	return False

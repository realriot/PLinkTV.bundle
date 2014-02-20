#!/usr/bin/python
import urllib, urllib2, simplejson
json = simplejson
debug = True

def apiRequestKippt(auth, call, args = None):
	url = "https://kippt.com" + call
	headers = { 'User-Agent' : 'Mozilla/5.0', 
		'X-Kippt-Username' : auth['username'],
		'X-Kippt-API-Token' : auth['token']
	}

	# Prepare request.
	data = None
	if args != None:
		data = urllib.urlencode(args)

	#req = urllib2.Request(url, data, headers)
	req = urllib2.Request(url, data, headers)

	# Execute request.
	response = urllib2.urlopen(req)
	result = response.read()
	return result

def getKipptFolders(auth):
	#if debug == True: Log("Using kippt auth: " + str(auth))
	try:
		tmp = apiRequestKippt(auth, "/api/folders/")
		json_data = json.loads(tmp)
		return json_data
	except Exception, e:
		if debug == True: Log("getKipptFolders() failed: " + str(e))
		return False

def getKipptLists(auth):
	#if debug == True: Log("Using kippt auth: " + str(auth))
	try:
		tmp = apiRequestKippt(auth, "/api/lists/")
		json_data = json.loads(tmp)
		return json_data
	except Exception, e:
		if debug == True: Log("getKipptLists() failed: " + str(e))
		return False

def getKipptClips(auth):
	#if debug == True: Log("Using kippt auth: " + str(auth))
	try:
		tmp = apiRequestKippt(auth, "/api/clips/")
		json_data = json.loads(tmp)
		return json_data
	except Exception, e:
		if debug == True: Log("getKipptClips() failed: " + str(e))
		return False

def getKipptFavoriteClips():
	#if debug == True: Log("Using kippt auth: " + str(auth))
	try:
		tmp = apiRequestKippt(auth, "/api/clips/favorites/")
		json_data = json.loads(tmp)
		return json_data
	except Exception, e:
		if debug == True: Log("getKipptFavoriteClips() failed: " + str(e))
		return False

import simplejson
from mod_kippt import *
from mod_delicious import *
json = simplejson

# Static text. 
APP_NAME = 'PLinkTV'
LOGO = 'logo.png'

# Image resources.
ICON_MAIN = 'logo.png'

# Other definitions.
PLUGIN_PREFIX = '/video/plinktv'
debug = True
debug_raw = True

# Init kippt data. 
auth_kippt = { 'username': '', 'token': '' }
kippt_folders = False
kippt_lists = False
kippt_clips = False
kippt_updated = False
kippt_thread = False

# Init Delicious data.
auth_delicious = {
	'username' : '',
	'password' : '',
	'delicious_clientid' : '',
	'delicious_clientsecret' : ''
}
auth_delicious_token = False
delicious_tags = False
delicious_posts = False
delicious_updated = False
delicious_thread = False

####################################################################################################

def Start():
	Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, APP_NAME, LOGO)
	HTTP.CacheTime = 1

	Thread.Create(kipptThread, globalize=True)
	Thread.Create(deliciousThread, globalize=True)

####################################################################################################

@handler('/video/plinktv', APP_NAME, thumb=ICON_MAIN)
def MainMenu():
	oc = ObjectContainer(no_cache=True)	
	kippt_objlist = []
	delicious_objlist = []

	if checkConfig():
		if debug == True: Log('Configuration OK!')
		oc.title1 = APP_NAME
		oc.header = L('info') 
		oc.message = L('info_no_content_found') 

		# Build structure for kippt.
		if kippt_updated == True:
			kippt_objlist = getKipptStructure()
			for obj in kippt_objlist:
				oc.add(obj)

		# Build structure for Delicious.
		if delicious_updated == True:
			delicious_objlist = getDeliciousStructure()
			for obj in delicious_objlist:
				oc.add(obj)

		# Remove information tags if the content isn't empty.
		if len(kippt_objlist) > 0 or len(delicious_objlist) > 0:
			oc.header = None
			oc.message = None

		# Add preferences.
		oc.add(PrefsObject(title=L('preferences')))
	else:
		if debug == True: Log('Configuration error! Displaying error message.')
		oc.title1 = None
		oc.header = L('error')
                oc.message = L('error_no_config')
		oc.add(PrefsObject(title=L('preferences')))

	return oc

####################################################################################################

def ValidatePrefs():
	global kippt_thread
	global delicious_thread

	# Handle kippt.
	if Prefs['kippt_use'] == True:
		if kippt_thread == False:
			Thread.Create(kipptThread, globalize=True)
	else:
		if kippt_thread == True:
			kippt_thread = False

	# Handle Delicious.
	if Prefs['delicious_use'] == True:
		if delicious_thread == False:
			Thread.Create(deliciousThread, globalize=True)
	else:
		if delicious_thread == True:
			 delicious_thread = False

def checkConfig():
	global auth_kippt
	global auth_delicious
	result = False

	try:
		# Check settings for kippt.
		if Prefs['kippt_use'] == True:
			if Prefs['kippt_username'] != "" and Prefs['kippt_apitoken'] != "":
				auth_kippt['username'] = Prefs['kippt_username']
				auth_kippt['token'] = Prefs['kippt_apitoken']
				result = True
			else:
				return False

		# Check settings for delicious.
		if Prefs['delicious_use'] == True:
			if Prefs['delicious_username'] != "" and Prefs['delicious_password'] != "" and Prefs['delicious_client_id'] != "" and Prefs['delicious_client_secret'] != "":
				result = True
			else:
				return False			

		# Return error if we didn't configure anything.
		if Prefs['kippt_use'] == False and Prefs['delicious_use'] == False:
			return False
	except:
		return False 

	return result

####################################################################################################

def kipptThread():
	if debug == True: Log("******  Starting kippt thread  ***********")
	thread_sleep = int(Prefs['update_interval'])*60 
	global kippt_folders
	global kippt_lists
	global kippt_clips
	global kippt_updated
	global kippt_thread

	kippt_thread = True

	checkConfig()
	while (Prefs['kippt_use'] == True and kippt_thread == True):
		if debug == True: Log.Info("kipptThread() loop...")	
		try:
			kippt_folders = getKipptFolders(auth_kippt)
			kippt_lists = getKipptLists(auth_kippt)
			kippt_clips = getKipptClips(auth_kippt)
			kippt_updated = True
			if debug_raw == True: Log("Got kippt data:")
			if debug_raw == True: Log(kippt_folders)
			if debug_raw == True: Log(kippt_lists)
			if debug_raw == True: Log(kippt_clips)
		except Exception, e:
			if debug == True: Log("Talking to kippt api failed: " + str(e))
			kippt_folders = False
			kippt_lists = False
			kippt_clips = False
			kippt_updated = False
		if debug == True: Log("****** kippt thread sleeping for " + str(thread_sleep) + " seconds ***********")
		Thread.Sleep(float(thread_sleep))

	if debug == True: Log("Exiting kippt thread....")
	kippt_thread = False
	kippt_folders = False
	kippt_lists = False
	kippt_clips = False
	kippt_updated = False

####################################################################################################

def deliciousThread():
	if debug == True: Log("******  Starting Delicious thread  ***********")
	thread_sleep = int(Prefs['update_interval'])*60
	global delicious_tags
	global delicious_posts
	global delicious_updated
	global delicious_thread

	delicious_thread = True
	
	checkConfig()
	while (Prefs['delicious_use'] == True and delicious_thread == True and Prefs['delicious_username'] != "" and Prefs['delicious_password'] != "" and Prefs['delicious_client_id'] != "" and Prefs['delicious_client_secret'] != ""):
		if debug == True: Log.Info("deliciousThread() loop...")
		try:
			token = getDeliciousToken(Prefs['delicious_username'], Prefs['delicious_password'], Prefs['delicious_client_id'], Prefs['delicious_client_secret'])
			delicious_tags = getDeliciousTags(token)
			delicious_posts = getDeliciousPosts(token)
			delicious_updated = True
		except Exception, e:
			if debug == True: Log("Talking to Delicious api failed: " + str(e))
			delicious_tags = False
			delicious_posts = False
			delicious_updated = False
		if debug == True: Log("****** Delicious thread sleeping for " + str(thread_sleep) + " seconds ***********")
		Thread.Sleep(float(thread_sleep))

	if debug == True: Log("Exiting Delicious thread....")
	delicious_thread = False
	delicious_tags = False
	delicious_posts = False
	delicious_updated = False

####################################################################################################

def getKipptStructure(mode='folders', ids=None): 
	oc = ObjectContainer(no_cache=True)
	objlist = []
	# Add folder structure.
	if mode == 'folders':
		if debug == True: Log("Called getKipptStructure with mode FOLDERS")
		if kippt_folders != False and kippt_lists != False and kippt_clips != False:
			for folder in kippt_folders:
				if folder['lists'] >= 1:
					if debug == True: Log("Adding Kippt folder: " + folder['title'])
					objlist.append(DirectoryObject(key=Callback(getKipptStructure, mode='lists', ids=folder['lists']), title=folder['title']))
					#oc.add(DirectoryObject(key=Callback(getKipptStructure, mode='lists', ids=folder['lists']), title=folder['title']))

	# Add list structure.
	if mode == "lists":
		if debug == True: Log("Called getKipptStructure with mode LISTS")
		for id in ids:
			if debug == True: Log("Adding Kippt listid to folder: " + str(id))

			# Get listname from listdata.
			listname = ""
			listid = ""
			for list in kippt_lists['objects']:
				if list['id'] == id:
					listname = list['title']
					listid = list['resource_uri']
			oc.add(DirectoryObject(key=Callback(getKipptStructure, mode='clips', ids=listid), title=listname))

	if mode == "clips":
		if debug == True: Log("Called getKipptStructure with mode CLIPS")
		for clip in kippt_clips['objects']:
			if clip['list'] == ids:
				oc.add(createKipptVideoObject(clip))

	if mode == 'folders':
		return objlist
	else:
		return oc

####################################################################################################

def getDeliciousStructure(mode='tags', tag=None):
	oc = ObjectContainer(no_cache=True)
	objlist = []
	# Add folder structure.
	if mode == 'tags':
		if debug == True: Log("Called getDeliciousStructure with mode TAGS")
		if delicious_tags != False and delicious_posts != False:
			for delicious_tag in delicious_tags:
				# Exclude tags as folders.
				if delicious_tag['tag'] != '!plex':
					if countDeliciousMediaWithTag(delicious_posts, delicious_tag['tag']) > 0:
						objlist.append(DirectoryObject(key=Callback(getDeliciousStructure, mode='posts', tag=delicious_tag['tag']), title=delicious_tag['tag']))
						#oc.add(DirectoryObject(key=Callback(getDeliciousStructure, mode='posts', tag=delicious_tag['tag']), title=delicious_tag['tag']))

	if mode == 'posts':
		if debug == True: Log("Called getDeliciousStructure with mode POSTS")
		for delicious_post in delicious_posts:
			if checkDeliciousMediaTag(delicious_post, tag):
				oc.add(createDeliciousVideoObject(delicious_post))

	if mode == 'tags':
		return objlist
	else:
		return oc

####################################################################################################

def createKipptVideoObject(mediaobject, container = False):
        if debug == True: Log("Creating kippt videoobject for url: " + mediaobject['url'])

        vco = VideoClipObject(
                key = Callback(createKipptVideoObject, mediaobject = mediaobject, container = True),
                rating_key = mediaobject['url'],
                title = mediaobject['title'],
                summary = mediaobject['notes'],
                items = [
                        MediaObject(
				container = Container.MP4,
				video_codec = VideoCodec.H264,
				audio_codec = AudioCodec.AAC,
                                parts = [PartObject(key = mediaobject['url'])]
                        )
                ]
        )
        if container:
                return ObjectContainer(objects = [vco])
        else:
                return vco
        return vco

####################################################################################################

def createDeliciousVideoObject(mediaobject, container = False):
	if debug == True: Log("Creating Delicious videoobject for url: " + mediaobject['href'])

	vco = VideoClipObject(
		key = Callback(createDeliciousVideoObject, mediaobject = mediaobject, container = True),
		rating_key = mediaobject['href'],
		title = mediaobject['description'],
		summary = mediaobject['extended'], 
		items = [
			MediaObject(
				container = Container.MP4,
				video_codec = VideoCodec.H264,
				audio_codec = AudioCodec.AAC,
				parts = [PartObject(key = mediaobject['href'])]
			)
		]
	)
	if container:
		return ObjectContainer(objects = [vco])
	else:
		return vco
	return vco

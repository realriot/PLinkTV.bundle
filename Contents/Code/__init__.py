import simplejson, datetime
from mod_helper import *
from mod_kippt import *
from mod_delicious import *
from mod_tmdb import *
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

# Init TMDb data.
tmdb_thread = False

####################################################################################################

def Start():
	Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, APP_NAME, LOGO)
	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
	Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
	HTTP.CacheTime = 1

	Thread.Create(kipptThread, globalize=True)
	Thread.Create(deliciousThread, globalize=True)
	Thread.Create(tmdbThread, globalize=True)

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
	global tmdb_thread

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

	# Handle TMDb.
	if Prefs['tmdb_use'] == True:
		if tmdb_thread == False:
			 Thread.Create(tmdbThread, globalize=True)
	else:
		if tmdb_thread == True:
			tmdb_thread = False

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
	if debug == True: Log("****** Starting kippt thread ***********")
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
			kippt_folders_tmp = getKipptFolders(auth_kippt)
			kippt_lists_tmp = getKipptLists(auth_kippt)
			kippt_clips_tmp = getKipptClips(auth_kippt)
			kippt_folders = kippt_folders_tmp
			kippt_lists = kippt_lists_tmp
			kippt_clips = kippt_clips_tmp
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
	if debug == True: Log("****** Starting Delicious thread ***********")
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
			delicious_tags_tmp = getDeliciousTags(token)
			delicious_posts_tmp = getDeliciousPosts(token)
			delicious_tags = delicious_tags_tmp
			delicious_posts = delicious_posts_tmp
			if debug_raw == True: Log("Got Delicious data:")
                        if debug_raw == True: Log(delicious_tags)
			if debug_raw == True: Log(delicious_posts)
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

def tmdbThread():
	if debug == True: Log("****** Starting TMDb thread ***********")
	thread_sleep = 60
	global kippt_clips
	global delicious_posts

	tmdb_thread = True
	while (Prefs['tmdb_use'] == True and tmdb_thread == True and Prefs['tmdb_apikey'] != ""):
		if debug == True: Log.Info("tmdbThread() loop...")
		try:
			# Fetch TMdb data for kippt movies.
			if kippt_clips != False:
				for clip in kippt_clips['objects']:
					if hasPlexMovieTag(clip['notes']) == True:
						if debug == True: Log("Looking up clip at tmdb: " + clip['title'])
						if clip['url'] in Dict:
							if debug == True: Log("TMDb data already exists for: " + clip['title'])
						else:
							data = tmdbSearchMovie(Prefs['tmdb_apikey'], Prefs['tmdb_language'], clip['title'])
							if data != False:
								Dict[clip['url']] = data
					else:
						if debug == True: Log("Clip has no tag which results in TMDb lookup.")
						if clip['url'] in Dict:
							if debug == True: Log("Deleting TMDb cache for url: " + clip['url'])
							Dict[clip['url']] = None
							if debug_raw == True: Log(Dict[clip['url']])
			
			# Fetch TMDb data for Delicious movies.
			if delicious_posts != False:
				for delicious_post in delicious_posts:
					if hasPlexMovieTag(delicious_post['extended']) == True:
						if debug == True: Log("Looking up clip at tmdb: " + delicious_post['description'])
						if delicious_post['href'] in Dict:
							if debug == True: Log("TMDb data already exists for: " + delicious_post['description'])
						else:
							data = tmdbSearchMovie(Prefs['tmdb_apikey'], Prefs['tmdb_language'], delicious_post['description'])
							if data != False:
								Dict[delicious_post['href']] = data
					else:
						if debug == True: Log("Clip has no tag which results in TMDb lookup.")
						if delicious_post['href'] in Dict:
							if debug == True: Log("Deleting TMDb cache for url: " + delicious_post['href'])
							Dict[delicious_post['href']] = None
							if debug_raw == True: Log(Dict[delicious_post['href']])
		except Exception, e:
			if debug == True: Log("Talking to tmdb api failed: " + str(e))
		if debug == True: Log("****** Delicious thread sleeping for " + str(thread_sleep) + " seconds ***********")
		Thread.Sleep(float(thread_sleep))

	if debug == True: Log("Exiting TMDb thread....")
	tmdb_thread = False 

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
				videometadata = { 'url': clip['url'],
						'title': clip['title'],
						'summary': clip['notes']
				}
				oc.add(createVideoObject(videometadata))

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
		Log(delicious_tags)
		if delicious_tags != False and delicious_posts != False:
			for delicious_tag in delicious_tags:
				# Exclude tags as folders.
				if delicious_tag['tag'] != '!plex' and delicious_tag['tag'] != '!plexmovie':
					if countDeliciousMediaWithTag(delicious_posts, delicious_tag['tag']) > 0:
						objlist.append(DirectoryObject(key=Callback(getDeliciousStructure, mode='posts', tag=delicious_tag['tag']), title=delicious_tag['tag']))
						#oc.add(DirectoryObject(key=Callback(getDeliciousStructure, mode='posts', tag=delicious_tag['tag']), title=delicious_tag['tag']))

	if mode == 'posts':
		if debug == True: Log("Called getDeliciousStructure with mode POSTS")
		for delicious_post in delicious_posts:
			if checkDeliciousMediaTag(delicious_post, tag):
				videometadata = { 'url': delicious_post['href'],
						'title': delicious_post['description'],
						'summary': delicious_post['extended']
				}
				oc.add(createVideoObject(videometadata))

	if mode == 'tags':
		return objlist
	else:
		return oc

####################################################################################################

def createVideoObject(videometadata, container = False):
	if debug == True: Log("Creating videoobject for url: " + videometadata['url'])

	vo = VideoClipObject(
		key = Callback(createVideoObject, videometadata = videometadata, container = True),
		rating_key = videometadata['url'],
		items = [
			MediaObject(
				container = Container.MP4,
				video_codec = VideoCodec.H264,
				audio_codec = AudioCodec.AAC,
				parts = [PartObject(key = videometadata['url'])]
			)
		]
	)

	if videometadata['url'] in Dict and Dict[videometadata['url']] != None:
		vo = MovieObject(
			key = Callback(createVideoObject, videometadata = videometadata, container = True),
			rating_key = videometadata['url'],
			items = [
			]
		)
		mo = MediaObject(parts = [PartObject(key = videometadata['url'])])

		# Handle media configuration via summary.
		mediaconfig = getMediaLinkConfig(videometadata['summary'])
		if mediaconfig != False:
			if mediaconfig['vcodec'] == 'h264':
				mo.video_codec = VideoCodec.H264

			if mediaconfig['acodec'] == 'aac':
				mo.audio_codec = AudioCodec.AAC
			elif mediaconfig['acodec'] == 'mp3':
				mo.audio_codec = AudioCodec.MP3
			else:
				mo.audio_codec = AudioCodec.AAC

			if mediaconfig['container'] == 'mp4':
				mo.container = Container.MP4
			elif mediaconfig['container'] == 'mkv':
				mo.container = Container.MKV
			elif mediaconfig['container'] == 'mov':
				mo.container = Container.MOV
			elif mediaconfig['container'] == 'avi':
				mo.container = Container.AVI
			else:
				mo.container = Container.MP4
		else:
			mo.container = Container.MP4
			mo.video_codec = VideoCodec.H264
			mo.audio_codec = AudioCodec.AAC
	
		vo.items.append(mo)
	
		tmdbdata = Dict[videometadata['url']]
		# Prepare genres.
		genres = []
		for genre in tmdbdata['genres']:
			genres.append(genre['name'])

		# Prepare production countries.
		countries = []
		for country in tmdbdata['production_countries']:
			countries.append(country['name'])

		vo.thumb = "http://image.tmdb.org/t/p/w342" + tmdbdata['poster_path']
		vo.art = "http://image.tmdb.org/t/p/w500" + tmdbdata['backdrop_path']
		vo.title = tmdbdata['title']
		vo.tagline = tmdbdata['tagline']
		vo.summary = tmdbdata['overview']
		vo.duration = int(tmdbdata['runtime'])*60000
		vo.rating = float(tmdbdata['vote_average'])
		vo.genres = tmdbdata['genres'] 
		vo.original_title = tmdbdata['original_title']
		vo.year = datetime.datetime.strptime(tmdbdata['release_date'], '%Y-%m-%d').year
		vo.originally_available_at = datetime.datetime.strptime(tmdbdata['release_date'], '%Y-%m-%d') 
		vo.countries = countries
 
	else:
		vo.title = videometadata['title']
		vo.summary = re.sub('\$plex\[.*\]', '', videometadata['summary'])

        if container:
                return ObjectContainer(objects = [vo])
        else:
                return vo
        return vo

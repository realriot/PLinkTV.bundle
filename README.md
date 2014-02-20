PLinkTV is a plex channel which delivers your kippt and Delicious content to your plex
devices.

Please keep in mind that this channel will _not transcode_ any content. So you have to make sure
that the content is viewable on your devices. If plex will support any transcoding of streamed
content in the future, this feature can be implemented afterwards.

Kippt support:
You have to fetch your private api token from: http://developers.kippt.com/#apitoken
The username and token will be used within the channel settings to authenticate against the
kippt service. You will be able to browse through all folders and lists.

Delicious support:
Get your Declicious api key from here: https://delicious.com/settings/developer
You'll get a "Client ID" and "Client Secret" which has to be configured within the
channel settings including username and password. This secret data is used for oauth 2.0 purposes.
To include your media links in your plex structure you have to add a special tag to your
links. As you can imagine the plex tag will be: !plex

themoviedb.org support:
Lookup your personal API Key within your account details at: https://www.themoviedb.org/login
You have to enter this key within the channel settings. A movie will get a lookup if you specify
a movie tag to your $plex clip-configuration. See the additional informations below.

Additional information:
You can enter "notes" at kippt.com and "comments" at delicious.com for each clip. Within these
lines you can add a special configuration string which will be handled by this channel. Please sponsor
a whole line for this string so the channel can filter it out afterwards.

Syntax: $plex[_media type_,_video codec_,_audio codec_,_container type_]
For example: $plex[movie,h264,aac,mp4]

The following values can be used. Everything else will be ignored:
_media type_
   movie
   tvseries
   clip

_video codec_
   h264

_audio codec_
   aac
   mp3
   ac3

_container type_
   mp4
   mkv
   mov
   avi

If you choose "movie" as mediatype the TMDb support will lookup this movie and add the found
meta informations.

PLinkTV is a plex channel which delivers your kippt and Delicious content to your plex
devices.

Kippt
You have to fetch your private api token from: http://developers.kippt.com/#apitoken
The username and token will be used within the channel settings to authenticate against the
kippt service. You will be able to browse through all folders and lists. 

Delicious
Get your Declicious api key from here: https://delicious.com/settings/developer
You'll get a "Client ID" and "Client Secret" which has to be configured within the
channel settings including username and password. This secret data is used for oauth 2.0 purposes.
To include your media links in your plex structure you have to add a special tag to your
links. As you can imagine the plex tag will be: !plex

Please keep in mind that this channel will _not transcode_ any content. So you have to make sure
that the content is viewable on your devices. If plex will support any transcoding of streamed
content in the future, this feature can be implemented afterwards.

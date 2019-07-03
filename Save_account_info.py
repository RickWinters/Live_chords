import json
import os

username = "YOUR USERNAME HERE"
scope = 'user-read-currently-playing user-modify-playback-state'

clientid =     'YOUR CLIENT ID HERE'
clientsecret = 'YOUR CLIENT SECRET HERE'
redirect_uri = 'http://google.com/' #USE THIS LINK IN YOUR SPOTIFY API APP AS THE CALLBACK URI

data = {}
data['username'] = username
data['scope'] = scope
data['clientid'] = clientid
data['clientsecret'] = clientsecret
data['redirect_uri'] = redirect_uri

text = json.dumps(data)

accountinfo = open("./account_info.txt","w")
accountinfo.write(text)
accountinfo.close()

#test
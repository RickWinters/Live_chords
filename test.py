import json
import os

username = 'rickwinters12'
scope = 'user-read-currently-playing user-modify-playback-state'

clientid = 'cb3d87487c3f45678e4f28c0f1787d59'
clientsecret = '720cb763c5114ce581303e30846d962d'
redirect_uri = 'http://google.com/'

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

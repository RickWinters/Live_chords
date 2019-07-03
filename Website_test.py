import json

import requests

from live_chords import get_current_song

account_info = json.loads(open("./account_info.txt").read())
username = account_info['username']
scope = account_info['scope']
clientid = account_info['clientid']
clientsecret = account_info['clientsecret']
redirect_uri = account_info['redirect_uri']

title, artist, t0 = get_current_song(username, clientid, clientsecret, redirect_uri)

searchurl = "http://localhost:8080/live_chords/Get/{}/{}".format(artist.replace(" ", "_"), title.replace(" ", "_"))
r = requests.get(searchurl)
data = r.text
data = json.loads(data)
# datafile = file.

print(data)

import spotipy
import spotipy.util as util

#get username from terminal
#https://open.spotify.com/user/rickwinters?si=2yDwr48JQDygt754Xv6pJA
# USER ID rickwinters?si=ACYhltU_Rcu_ZpFHRiXApg
username = 'rickwinters12'
scope = 'user-read-currently-playing'

clientid = 'cb3d87487c3f45678e4f28c0f1787d59'
clientsecret =  '720cb763c5114ce581303e30846d962d'
redirect_uri = 'http://google.com/'
#Erase cache and prompt for user permission
#util.prompt_for_user_token(username,scope,client_id='cb3d87487c3f45678e4f28c0f1787d59',client_secret='720cb763c5114ce581303e30846d962d',redirect_uri='http://google.com')
token = util.prompt_for_user_token(username, scope, client_id=clientid, client_secret=clientsecret, redirect_uri=redirect_uri)

sp = spotipy.Spotify(auth=token)
song = sp.current_playing()
title = song['item']['name']
artist = song['item']['artists'][0]['name']

print("currently playing: " + title + " by " + artist)





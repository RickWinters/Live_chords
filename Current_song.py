import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import sys

scope = 'user-library-read'

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print("usage: %s username" % sys.argv[0])
    sys.exit()

token = util.prompt_for_user_token(username, scope)

if token:
    sp = spotipy.Spotify(auth=token)
    results = sp.current_user_saved_tracks()
    for item in results['items']:
        track = item['track']
        print(track['name'] + ' - ' + track['artists'][0]['name'])
else:
    print("cant get token for" + username)

    # cb3d87487c3f45678e4f28c0f1787d59

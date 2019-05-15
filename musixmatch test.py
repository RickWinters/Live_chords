from live_chords import get_current_song
import Musixmatch_api
import requests
import json
from Musixmatch_api import base_url, lyrics_matcher, track_matcher, format_url, artist_search_parameter, track_search_parameter, api_key, richsync_matcher, track_id_parameter
# base_url
# track_matcher
# format_url
# artist_search_parameter
# track_search_parameter
# api_key

def main():
    username = 'rickwinters12'
    scope = 'user-read-currently-playing'

    clientid = 'cb3d87487c3f45678e4f28c0f1787d59'
    clientsecret = '720cb763c5114ce581303e30846d962d'
    redirect_uri = 'http://google.com/'

    title, artist = get_current_song(username, clientid, clientsecret, redirect_uri)


    #see if musixmatch has lyrics
    api_call = base_url + track_matcher + format_url + artist_search_parameter + artist + track_search_parameter + title + api_key
    print(api_call)
    request = requests.get(api_call)
    data = request.json()
    data = data['message']['body']['track']

    has_lyrics = data['has_lyrics']
    has_richsync = data['has_richsync']
    track_id = data['track_id']

    if has_lyrics:
        print("track has lyrics")
    else:
        print("track has no lyrics")
    if has_richsync:
        print("track has richsync")
    else:
        print("track has no richsync")
    print("track id = " + str(track_id))

    if has_richsync:
        print("searching for synced lyrics")
        track_id_string = str(track_id)
        api_call = base_url + richsync_matcher + track_id_parameter + "114837375" + api_key
        request = requests.get(api_call)
        data = request.json()
        print(data)
    if has_lyrics:
        print("searching for lyrics")
        api_call = base_url + lyrics_matcher + format_url + artist_search_parameter + artist + track_search_parameter + title + api_key
        request = requests.get(api_call)
        data = request.json()
        lyrics_body = data['message']['body']['lyrics']['lyrics_body']
        script_tracking_url = data['message']['body']['lyrics']['script_tracking_url']
        request = requests.get(script_tracking_url)
        data = request.text
        print(data)



if __name__ == "__main__":
    main()


















"""
Wile True:
    print()
    print("Welcome to blablababla")
    print()
    print("menu options")
    print("1 - Call one of the  API methods with parameters and see JSON")
    print("2 - Search for the lyrics of a song")
    print("3 - Exit")
    choice = '1'
    print ()

    if choice == '0':
        break

    if choice == '1': # see the parameters ofr an api method
        print("API METHODS")
        for index, api_method in enumerate(api_methods, start=0):
            print(str(index) + ": " + api_method)
        print()
        print("Your choice (0 - 15)")
        method_choice = input("> ")
        print()
        user_choice = api_methods[int(method_choice)]
        parameter_list = get_parameters(user_choice)

        print("PARAMATERS")
        for index, parameter in enumerate(parameter_list, start=0):
            print(str(index) + ": " + parameter)
        print()

        # start building the api call
        api_call = base_url + user_choice + format_url

        while True:
            print("API call so far: " + api_call)
            print()
            print("Which parameter would you like to add a value for? (0-n) (type x to make the call)")
            parameter_choice = input("> ")
            print()

            # add the api key and make the call
            if parameter_choice == "x":
                api_call = api_call + api_key
                request = requests.get(api_call)
                data = request.json()
                print("Final API Call: " + api_call)
                print()
                print("JSON DATA")
                print(json.dumps(data, sort_keys=True, indent=2))
                break

            # add a parameter
            else:
                parameter_choice_string = parameter_list[int(parameter_choice)]
                value = input(parameter_choice_string)
                api_call = api_call + parameter_choice_string + value
                print()

    if choice == '2':#example
        print("artist?")
        artist_name = "flogging molly"
        print("track title?")
        track_name = "the last serenade"
        print()
        api_call = base_url + lyrics_matcher + format_url + artist_search_parameter + artist_name + track_search_parameter + track_name + api_key
        #api_call = api_call.replace(" ","%20")
        print(api_call)
        #call the api
        request = requests.get(api_call)
        data = request.json()
        data = data['message']['body']
        print("API CALL: " + api_call)
        print()
        print(data['lyrics']['lyrics_body'])


    print()
    print("Again? (y/n)")
    again = input("> ")
    if again == "n":
        break
"""














# API key: 1754dba86b62cd339e561ed0984169fb

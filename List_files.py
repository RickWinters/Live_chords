import os
import json

import requests

from live_chords import version

print("List files locally or on server?")
print("1: locally")
print("2: on server")
choice = input("-->: ")

if choice == "2":
    print("Server Connection type?")
    print("1: localhost")
    print("2: remote server")
    server = input("-->: ")
    if server == "1":
        serverurl = "http://localhost:8080/live_chords"
    elif server == "2":
        serverurl = "192.168.1.111:8080/live_chords"

    files = requests.get(server + "/list").text

if choice == "1":
    path  = "./tabs/"

    files = []
    oldversion = []
    synced = []
    ready = []
    incomplete = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            if '.txt' in file:
                files.append(os.path.join(r, file))

for f in files:
    file = json.loads(open(f).read())
    string = file['artist'].replace("%20", " ") + ' - ' + file['title'].replace("%20", " ")
    if (not 'version' in file) or (file['version'] != version):
        oldversion.append(string)
    elif file['synced']:
        synced.append(string)
    elif file['has_tabs'] and file['has_azlyrics']:
        ready.append(string)
    else:
        incomplete.append(string)

print("Synced:")
for song in synced:
    print(song)

print("\n\n\n\n not synchronised but ready")
for song in ready:
    print(song)

print("\n\n\n\n incomplete songs")
for song in incomplete:
    print(song)

print("\n\n\n\n Tabs from older version")
for song in oldversion:
    print(song)
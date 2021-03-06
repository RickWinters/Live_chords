# -*- coding: utf-8 -*-

import datetime
import json
import os
import time
import urllib.error
import urllib.request
from difflib import SequenceMatcher

import lyricsgenius
import requests
from bs4 import BeautifulSoup

import spotipy
import spotipy.util as util

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def cleanArtistTitleString(artist, title):
    title = title.replace("acoustic", "")
    title = title.replace("Acoustic", "")
    title = title.replace("-", "")
    title = title.replace("(", "")
    title = title.replace(")", "")
    title = title.replace("live", "")
    title = title.replace("Live", "")
    title = title.replace("\'", "")
    title = title.replace("Version", "")
    title = title.replace("version", "")
    title = title.replace(".", "")
    title = title.replace("é", "e")
    title = title.replace("ê", "e")
    title = title.replace("mono", "")
    title = title.replace("Mono", "")
    title = title.replace("Remastered","")
    title = title.replace("remastered","")
    title = title.replace("Remaster","")
    title = title.replace("remaster","")
    artist = artist.replace("?", "")
    artist = artist.replace("!", "")
    artist = artist.replace("'", "")

    title = title.strip()
    artist = artist.strip()

    return artist, title

# Get current song playing from spotify
def get_current_song(username, clientid, clientsecret, redirect_uri, scope='user-read-currently-playing', printconsole = True):
    # get acces token by logging in or get it from cache
    if __name__ != "__main__":
        if printconsole: print("SEARCHING FOR SONG NOW AT " + str(datetime.datetime.now().time()))
    token = util.prompt_for_user_token(username, scope, client_id=clientid, client_secret=clientsecret,
                                       redirect_uri=redirect_uri)
    # create spotipy object
    sp = spotipy.Spotify(auth=token)

    # call the function currently playing. The standard spotipy python file does not have this function. Edit the source file by adding the following function:
    # "def current_playing()
    #   return self._get('me/player/currently-playing')
    # "
    song = sp.current_playing()  # returns json dict containing song info
    if song is not None and song['item'] is not None:
        title = song['item']['name']  # extract the current song title
        t0 = song['progress_ms'] / 1000
        artist = song['item']['artists'][0]['name']  # extracte the song artist
        artist, title = cleanArtistTitleString(artist, title)
    else:
        title = "no song playing"
        artist = "no song playing"
        t0 = 0

    # print("currently playing: " + title + " by " + artist)
    return title, artist, t0

# the input is a single string, this function seperates the multiple lines outputting an array of strings, where every index is a new line
def seperate_lines(data, tabslines=False):
    # Seperate the HTML text in multiple lines of text, skipping the newline tag
    data = data + "\n" #add a newline character to data so that the last line is picked up as well.
    string = " "  # generate empty string
    strings = []  # list of lines
    for char in data:  # for every character in the data
        if char == "\n":  # if it's a new line, put the existing string in the list, empty the existing string.
            if tabslines: #if the inputted string is from ultimate guitar tabs, replace \r and \\ with nothing.
                string = string.replace("\r", "")
                string = string.replace("\\", "")
            strings.append(string)
            string = ""
        else:
            string = string + char  # if its not a new line, add the current character to the string
    return strings  # return list of strings

# Input is string array of HTML of website with tabs, outputs a string with the tabs.
def extract_tabs(strings):
    # Loop over all the lines and extract the content json file, which contains the tabs.
    content = " "
    for string in strings:
        if string[4:27] == "window.UGAPP.store.page":  # find the correct line where the json data is stored
            content = string[30:-1]  # extract data
            break

    # Put the content tabs json file in a dictionary
    tabs = "no tabs found"
    if not content == " ":
        data = json.loads(content)  # convert json file to python dictionary
        # print(data)
        if "content" in data["data"]["tab_view"]["wiki_tab"]:
            tabs = data["data"]["tab_view"]["wiki_tab"]["content"]  # extract the tab text
            tabs = tabs.replace("[ch]", "")  # remove these characters
            tabs = tabs.replace("[/ch]", "")
    return tabs

# Extract the search results for ultimate guitar tabs search
def extract_search_results(strings):
    content = ""
    for string in strings:
        if string[4:27] == "window.UGAPP.store.page":  # List of search results are here
            content = string[29:-1]
            break

    data = json.loads(content)  # create dictionary from string

    if ('not_found' in data['data']) and (data['data']['not_found'] == True):
        data = "no data found"
    else:
        data = json.loads(content)  # convert stringed json file to python dict
        data = data["data"]["results"]  # extract search results
    # print(data)

    return data

# Print the search results to the console
def sort_search_results(data):
    # while loop that loops over all the results and checks if it contains chords or tabs. If there are results which are not tabs or chords these results are popped.
    tab_url = "no data found"

    i = 0  # iterator
    while i < len(data) and len(data) > 0:
        result = data[i]
        if "type" in result:
            if result['type'].lower() == "chords":
                i += 1
            else:
                data.pop(i)
        else:
            data.pop(i)

    # Sort remaining search results by highest rating.

    if len(data) > 0:
        highest_rating = 0
        if len(data) > 1:
            for result in data:
                if result["rating"] >= highest_rating:
                    highest_rating = result["rating"]
                    tab_url = result["tab_url"]
        else:
            tab_url = data[0]['tab_url']

    return tab_url  # return tab_url

# Print tabs to console
def print_tabs(file):
    if file.has_azlyrics and file.has_tabs:
        for line in file.chorded_lyrics:
            if line['group'] == 'intro' or line['group'] == 'start':
                print(line['lyrics'])
            else:
                if line['chords'] != "": print("chords: " + line['chords'])
                if line['lyrics'] != "": print("lyrics: " + line['lyrics'])
    elif file.has_tabs and not file.has_azlyrics:
        for line in file.tabslines:
            print(line['text'])

def search_ultimate_guitartabs(artist, title, print_to_console, printconsole):
    tabs = "no data found"
    found = False  # to keep track if the lyrics have been found or not
    # URL to search the website
    artist = artist.replace("%20"," ")
    artist = artist.replace("_"," ")
    title = title.replace("%20"," ")
    title = title.replace("_"," ")
    searchurl = "https://www.ultimate-guitar.com/search.php?search_type=title&value=" + artist + "%20" + title
    if printconsole: print(searchurl)
    r = requests.get(searchurl)
    data = r.text  # Pure HTML as single string
    searchhtml = seperate_lines(data)  # seperate the lines by searching for the newline tag
    search_results = extract_search_results(searchhtml)
    if search_results != "no data found":
        found = True
    else:
        if printconsole: print("NO SEARCH RESULTS FOUND ON ULTIMATE GUITAR TABS")

    if found:
        if printconsole: print("GETTING LYRICS FROM ULTIMATE GUITAR TABS")
        url = sort_search_results(search_results)  # print search results, and get the url of the highest rating result
        if url != "no data found":
            if printconsole: print(url)
            r = requests.get(url)  # get the website for the search result
            data = r.text  # HTMLtext
            htmldata = seperate_lines(data)  # seperated lines
            tabs = extract_tabs(htmldata)  # extracted the tabs line
            if print_to_console:
                print_tabs(tabs)  # print the tabs, slowly scrolling (maybe)

    return tabs

def search_azlyrics(artist, title, printconsole = True):
    if printconsole: print("STARTING SEARCH ON AZLYRICS")
    azlyrics = ["no azlyrics found"]  # if no azlyrics are found, this string will remain the same so that other functions know no azlyrics are found
    azartist = artist.lower()
    azartist = azartist.replace("%20", "+")
    aztitle = title.lower()
    aztitle = aztitle.replace("%20", "+") #on azlyrics the artist and title need to be formatted as "flogging+molly+life+is+good".
    url = "https://search.azlyrics.com/search.php?q={}+{}".format(azartist, aztitle)  # search on azlyrics
    if printconsole: print(url)
    r = requests.get(url)
    data = r.text
    lines = seperate_lines(data)
    found = False
    for line in lines:  # go through the html data from searching azlyrics and find the first result.
        if line.replace(" ", "")[0:2] == "1.":
            if printconsole: print(line) #the link is found between the quotes
            ind1 = line.find('"')
            ind2 = line[ind1 + 1:-1].find('"')
            link = line[ind1 + 1:ind2 + ind1 + 1]
            if printconsole: print(link)
            found = True
            break
    if found:
        r = requests.get(link)  # get the first result and extract the lyrics
        data = r.text
        lyrics = extract_lyrics(data)
        azlyrics = seperate_lines(lyrics[0])
        azlyrics.append("str")
    else:
        if printconsole: print("NO RESULTS FOUND ON AZLYRICS")

    return azlyrics

def search_genius(artist, title, printconsole = True):
    if printconsole: print("STARTING SEARCH ON GENIUS.COM")
    artist, title = cleanArtistTitleString(artist, title)
    artist = artist.replace("%20", " ")
    artist = artist.replace("_", " ")
    title = title.replace("%20", " ")
    title = title.replace("_", " ")
    genius = lyricsgenius.Genius("KuYRMCOBfjMrfi29BOpFq8daC-zj0DUnm3VPExaFQ4-eTJZIVF8bJJmUIz8wkJ7c")
    song = genius.search_song(title, artist, printconsole = printconsole)
    if (song is not None) and (similar(song.artist, artist) > 0.5 and similar(song.title, title))> 0.5:
        lyrics = seperate_lines(song.lyrics)
    else:
        lyrics = ["no azlyrics found"]

    return lyrics

# Find the lyrics and tabs for a artsist,title. Firstly looking at both artist and title than, if nothing found, only looking at title of song.
def search_lyrics(artist, title, print_to_console=False, printconsole = True):
    tabs = "no data found"
    azlyrics = ["no azlyrics found"]
    if printconsole: print("STARTING SEARCH ON ULTIMATE GUITAR TABS")
    tabs = search_ultimate_guitartabs(artist, title, print_to_console, printconsole)
    if tabs != "no data found":
        azlyrics = search_genius(artist, title, printconsole)
        if azlyrics == ["no azlyrics found"]:
            azlyrics = search_azlyrics(artist, title, printconsole)
        if printconsole: print("DONE WITH SEARCHING")
    else:
        if printconsole: print("stopping with searching, as no tabs are found")

    return tabs, azlyrics

# File class, This class has functions to open and save a file for the lyrics. The idea is that if the song has been downloaded before lyrics, tabdata and sync data will be saved to disk so that it can be opened quickly.
# methods in this class are:
#   'open_file()': checks if a file exists on disk, if not the search_lyrics function is called.
#   'close_file()': the data in the class is written to a json string file and the file is closed.
#   'to_dict()': Write all the class variables to the dictionary
#   'from_dict()': write all
class file:
    def __init__(self, artist, title, version, server, PrintToConsole = True):
        self.artist = artist
        self.title = title
        self.data = {}  # dictionary contains all class-variables as well in order to write them to json string file
        self.tabs = ""
        self.synced = False
        self.tabslines = []
        self.azlyrics = ""
        self.has_tabs = False
        self.has_azlyrics = False
        self.chorded_lyrics = []
        self.script_version = version
        self.file_version = ""
        self.to_dict()
        self.server = server
        self.printconsole = PrintToConsole

    def to_dict(self, update=False):  # helper function to write all the instance variables to the dictionary
        self.data['artist'] = self.artist
        self.data['title'] = self.title
        self.data['tabs'] = self.tabs
        if not update: self.data['synced'] = self.synced
        self.data['tabslines'] = self.tabslines
        self.data['azlyrics'] = self.azlyrics
        self.data['has_tabs'] = self.has_tabs
        self.data['has_azlyrics'] = self.has_azlyrics
        self.data['chorded_lyrics'] = self.chorded_lyrics
        self.data['version'] = self.script_version

    def from_dict(self): #when a file is loaded only the instance variable dictionary is loaded. This function loads values in.
        self.artist = self.data['artist']
        self.title = self.data['title']
        self.tabs = self.data['tabs']
        self.synced = self.data['synced']
        self.tabslines = self.data['tabslines']
        self.azlyrics = self.data['azlyrics']
        self.has_tabs = self.data['has_tabs']
        self.has_azlyrics = self.data['has_azlyrics']
        self.chorded_lyrics = self.data['chorded_lyrics']
        if 'version' in self.data:
            self.file_version = self.data['version']

    def clear_file(self, update=False):
        if not update: self.data = {}  # dictionary contains all class-variables as well in order to write them to json string file
        self.tabs = ""
        if not update: self.synced = False
        self.tabslines = []
        self.azlyrics = ""
        self.has_tabs = False
        self.has_azlyrics = False
        self.chorded_lyrics = []
        self.file_version = ""
        self.to_dict()

    def open_file(self): #this functions opens a file from the title if it exists and otherwise searches online
        file_exists = False
        correct_version = True

        #Check for a file on the server, if a serverlocation is set
        if not self.server == "no_server":
            if self.printconsole: print("LOOKING FOR FILE ON SERVER")
            try:
                artist = self.artist
                title = self.title
                artist = artist.replace("%20", "_")
                title = title.replace("%20", "_")
                artist = artist.replace(" ","_")
                title = title.replace(" ","_")
                r = requests.get(self.server + "Get/{}/{}".format(artist, title))
                text = r.text
                self.data = json.loads(text)
                self.from_dict()
                file_exists = True;
            except:
                if self.printconsole: print("NO CONNECTION TO SERVER")
                self.tabs = "no_file_found"
                self.server = "no_server"

        #IF no server location is set, or the server has not found a file, look for it locally
        if self.tabs == "no_file_found" or self.server == "no_server":
            if self.printconsole: print("NO FILE FOUND ON SERVER")
            if self.printconsole: print("LOOKING FOR EXISTING FILE")
            file_exists = os.path.isfile(  # see if the file exists
                "./tabs/" + self.artist.replace("%20", "_") + "_" + self.title.replace("%20", "_") + ".txt")
            correct_version = True
            if file_exists:
                if self.printconsole: print("FILE FOUND")
                File = open("./tabs/" + self.artist.replace("%20", "_") + "_" + self.title.replace("%20", "_") + ".txt",
                            "r")
                text = File.read()
                File.close()
                self.data = json.loads(text)  # load the textfile into the dictionary data
                self.from_dict()  # load the dictionary data into the variables
                self.close_file()  # AND if it is not on the server, now try to save the local file locally or to the server immidietly

        # CHECK IF THE FILE IS OF THE CORRECT VERSION
        if self.file_version != self.script_version:
            self.clear_file()
            correct_version = False
            if self.printconsole: print("UPDATING TO NEWER VERSION")

        #If the file doesn't exist locally, or is of the wrong version, search on the internet and create the file
        if (not file_exists) or (not correct_version):
            if self.printconsole: print("FILE NOT FOUND")
            tabs, azlyrics = search_lyrics(self.artist, self.title, printconsole = self.printconsole) #searches on the internet for the tabs and azlyrics
            #if no tabs are found, the variable will be "no data found", and than its useless to do anything else
            if tabs != "no data found" or azlyrics != ["no azlyrics found"]:
                self.tabs = tabs
                tabslines = seperate_lines(tabs, tabslines=True)
                #Server will return a tabsfile with every value set to "no_file_found", if no file is found. These need to be deleted
                if len(self.azlyrics) == 1:
                    if self.azlyrics[0] == "no_file_found":
                        self.azlyrics.pop(0)
                if len(self.chorded_lyrics) == 1:
                    if self.chorded_lyrics[0]['lyrics'] == "no_file_found":
                        self.chorded_lyrics.pop(0)
                for line in tabslines:
                    self.tabslines.append(
                        {})  # append an empty dictionary to the tabslines, for each tabslines this dictionary keeps track of the raw text, if it is a keyword, and if it is lyrics or chords. #todo add a dictionary item + logic for actual 6 lines tabs
                    self.tabslines[-1]['text'] = line
                    self.tabslines[-1]['keyword'] = False
                    if ("chorus" in line.lower()) or ("verse" in line.lower()) or ("intro" in line.lower()) or (
                            # check for keywords in the line
                            "outro" in line.lower()) or ("interlude" in line.lower()) or ("bridge" in line.lower()) \
                            or ("instrumental" in line.lower()) or "break" in line.lower():
                        self.tabslines[-1]['keyword'] = True
                    self.tabslines[-1]['lyrics'] = False
                    self.tabslines[-1]['chords'] = False
                self.azlyrics = azlyrics
                self.has_azlyrics = True
                self.has_tabs = True
                if azlyrics == "no azlyrics found":
                    self.has_azlyrics = False
                if tabs == "no data found":
                    self.has_tabs = False
                if self.has_tabs and self.has_azlyrics:
                    self.compare_lyrics() #compare lyrics will analyze the tabslines for which lines are lyrics and which line is chords. this uses azlyrics as masterfile and marks any tabslines as lyrics when it is similar enough
                    self.group_on_keywords() #assign a group to every line by extending keywords to all following lines until the next keyword
                    self.sort_lyrics() #use all the tabslines to fill the 'chorded_lyrics', this is a group of lyrics chords belonging to this line. These can be printed to the screen as one single group.
                self.close_file()
        else:
            if self.printconsole: print("FOUND FILE ON SERVER")

    def close_file(self):
        if self.server != "no_server":
            self.artist = self.artist.replace(" ","_")
            self.artist = self.artist.replace("%20","_")
            self.title = self.title.replace(" ","_")
            self.title = self.title.replace("%20","_")
            self.to_dict()
            r = requests.post(self.server + "Save/", json=self.data)
            if r.status_code == 200:
                if self.printconsole: print("SAVE SUCCESFULL")
        else:
            self.to_dict()  # load the variables into the dictionary
            text = json.dumps(self.data)  # convert to json string
            file = open("./tabs/" + self.artist.replace("%20", "_") + "_" + self.title.replace("%20", "_") + ".txt",
                        "w")
            file.write(text)  # write file
            file.close()

    def compare_lyrics(self):
        if self.printconsole: print("START WITH COMPARING LYRICS")
        #this functions loops over all the strings in tabslines and finds which are lyrics and than assigns the previous line (of not already assigned to being lyrics) as chords
        i = 0
        l = len(self.tabslines)
        for tabline in self.tabslines:
            line1 = tabline['text'].lower()  # line of text coming from the
            line1 = normalize_line(line1)
            matched = False
            if line1 != "" and len(line1) > 5:
                j = 0
                for line2 in self.azlyrics[0:-2]:  # loop over all the lines in azlyrics
                    line2 = line2.lower()
                    line2 = normalize_line(line2)
                    j += 1
                    line2app = self.azlyrics[j].lower()  # check the next line as well, incase the lyrics in tabslines correspond with 2 lines of text in azlyrics
                    line2app = normalize_line(line2app)
                    similarity = similar(line1,line2)  # check similarity, so that "blowin'" and "blowing" can still be matched
                    ind = line2.find(line1[0:4])
                    partlinesimilarity = similar(line1, line2[ind:ind + len(line1)])
                    if partlinesimilarity > 0.5 or similarity > 0.5:  # if tabslines text is only part of the azlyrics than it matches as well or if the similarity is similar. TODO check if part of line2 is similar enough?
                        tabline['lyrics'] = True
                        if not self.tabslines[i - 1]['lyrics']:
                            self.tabslines[i - 1]['chords'] = True
                        matched = True
                        break
                    line2 = line2 + line2app
                    similarity = similar(line1,
                                         line2)  # check now if 2 lines of azlyrics are similar enough with one line of tabslines
                    ind = line2.find(line1[0:4])
                    partlinesimilarity = similar(line1, line2[ind:ind + len(line1)])
                    if partlinesimilarity > 0.5 or similarity > 0.5:
                        tabline['lyrics'] = True
                        if not self.tabslines[i - 1]['lyrics']:
                            self.tabslines[i - 1]['chords'] = True
                        matched = True
                        # self.azlyrics[j] = " "
                        break
            i += 1
        if self.printconsole: print("done with comparing lyrics")

    def group_on_keywords(self):
        if self.printconsole: print("START GROUPING ON KEYWORDS")
        group = "start"
        i = 0
        while i < len(
                self.tabslines):  # go over each tabslines, when a new keyword is seen, assing all following lines the same keyword
            line = self.tabslines[i]
            line['group'] = group

            if line['keyword']:
                line['group'] = group = line['text']
                line['lyrics'] = True
                if i < (len(self.tabslines) - 1) and self.tabslines[i + 1]['text'] == "":
                    self.tabslines[i + 1]['group'] = group
                    i += 1

            if line['text'] == "":
                self.tabslines.pop(self.tabslines.index(line))
                group = "verse"
                continue

            i += 1


        if self.printconsole: print("done with comparing on keywords")

    def sort_lyrics(self):
        if self.printconsole: print("START WITH SORTING THE LYRICS")
        introtext = ""
        inintro = False
        starttext = ""
        instart = False
        solotext = ""
        insolo = False
        inbreak = False

        i = 0
        while i < len(self.tabslines):
            line = self.tabslines[i]
            if "solo" in line['group'].lower() or 'instrumental' in line['group'].lower()\
                    or 'interlude' in line['group'].lower() or 'pre-verse' in line['group'].lower():
                insolo = True
                if line['text'] != "":
                    solotext += line['text'] + "\n"
            elif insolo:
                self.add_chorded_lyrics_line(solotext,"","solo")
                solotext = ""
                insolo = False

            if "intro" in line['group'].lower(): #if the tabslines are part of the intro, assing them regardless if they're lyrics or not.
                inintro = True
                if line['text'] == "":
                    self.tabslines[i]['group'] = "verse"
                else:
                    introtext += line['text'] + "\n"
            elif inintro:
                self.add_chorded_lyrics_line(introtext,"","intro")
                introtext = ""
                inintro = False

            if "start" in line['group'].lower():
                instart = True
                if line['text'] != "":
                    starttext += line['text'] + "\n"
            elif instart:
                self.add_chorded_lyrics_line(starttext,"","start")
                starttext = ""
                instart = False

            if "break" in line['group'].lower() and not (insolo or inintro or instart or inbreak):
                inbreak = True
                j = 0
                no_lyrics = True
                while i+j < len(self.tabslines) and ("break" in self.tabslines[i + j]['group'].lower()):
                    if self.tabslines[i + j]['lyrics'] == True and j > 0:
                        no_lyrics = False
                        break
                    else:
                        solotext += self.tabslines[i + j]['text'] + "\n"
                    j += 1
                if no_lyrics:
                    self.add_chorded_lyrics_line(solotext, "", "break")
                    i += j
            elif inbreak:
                solotext = ""
                inbreak = False

            if not (instart or inbreak or inintro or insolo):
                if line['lyrics']: #if the tabslines is past the lyrics, only group them if this line is a lyrics. Assign the previous line for chords
                    self.chorded_lyrics.append({})
                    self.chorded_lyrics[-1]['lyrics'] = line['text'] #assign lyrics from tabslines into chorded_lyrics
                    if self.tabslines[i - 1]['chords']: #if the previous line are chords, add them as well
                        self.chorded_lyrics[-1]['chords'] = self.tabslines[i - 1]['text']
                    else:
                        self.chorded_lyrics[-1]['chords'] = ""
                    self.chorded_lyrics[-1]['start'] = 0 #start and stop are used for syncing information.
                    self.chorded_lyrics[-1]['stop'] = 0
                    self.chorded_lyrics[-1]['group'] = line['group']
            i += 1


        #loop over all the lines to replace the tabs-tags in the chords with 4 spaces
        for line in self.chorded_lyrics:
            line['chords'] = line['chords'].replace("\t","    ")
        if self.printconsole: print("done with sorting the lyrics")

    def add_chorded_lyrics_line(self,lyrics,chords,group):
        self.chorded_lyrics.append({})
        self.chorded_lyrics[-1]['lyrics'] = lyrics
        self.chorded_lyrics[-1]['chords'] = chords
        self.chorded_lyrics[-1]['start'] = 0
        self.chorded_lyrics[-1]['stop'] = 0
        self.chorded_lyrics[-1]['group'] = group

    def setsyncedtrue(self):
        self.synced = True

def normalize_line(str):
    str = str.replace("%20", "")
    str = str.replace("'", "")
    str = str.replace(" ", "")
    str = str.replace(",", "")
    str = str.replace(".", "")
    str = str.replace("\r", "")
    str = str.replace("(", "")
    str = str.replace(")", "")
    return str

def format_lyrics(lyrics):
    formated_lyrics = "\n".join(lyrics)
    return formated_lyrics

def extract_lyrics(page):
    soup = BeautifulSoup(page, "html.parser")
    lyrics_tags = soup.find_all("div", attrs={"class": None, "id": None})
    lyrics = [tag.getText() for tag in lyrics_tags]
    return lyrics

def normalize_str(str):
    str = str.replace("%20", "")
    str = str.replace("\'", "")
    str = str.replace(".", "")
    str = str.replace("(", "")
    str = str.replace(")", "")
    str = str.lower()
    return str

class Azlyrics(object):

    def __init__(self, artist, music, printconsole):
        self.artist = artist
        self.music = music

    def normalize_artist_music(self):
        return normalize_str(self.artist), normalize_str(self.music)

    def url(self):
        if not self.artist and not self.music:
            self.artist = "rickastley"
            self.music = "nevergonnagiveyouup"
        url = "http://azlyrics.com/lyrics/{}/{}.html".format(*self.normalize_artist_music())
        if self.printconsole: print(url)
        return url

    def get_page(self):
        try:
            page = urllib.request.urlopen(self.url())
            return page.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                if self.printconsole: print("Music not found")
                page = "no azlyrics found"
                return page

    def format_title(self):
        return "{} by {}".format(self.music.title(), self.artist.title())

    def get_lyrics(self):
        page = self.get_page()
        if page == "no azlyrics found":
            lyrics = page
        else:
            lyrics = extract_lyrics(page)
        return lyrics

def select_account():
    file = open("accounts.txt").read()

    accounts = []
    if not file == "":
        accounts = json.loads(file)
    correct = False
    while not correct:
        print("SELECT ACCOUNT TO LOG INTO, OR select '0' to create a new one")
        for account in accounts:
            print("{}: --> {}".format(account['number'],account['name']))
        accountnumber = (input("?:-->  "))

        try:
            accountnumber = int(accountnumber)
            if accountnumber == 0:
                new_account = {}
                new_account['spotify_id'] = input("Spotify id = ?:--> ")
                new_account['name'] = input("Name to display = ?:--> ")
                new_account['number'] = len(accounts) + 1
                name = new_account['spotify_id']
                if len(accounts) == 0:
                    accounts = []
                accounts.append(new_account)
                file = open("accounts.txt","w")
                file.write(json.dumps(accounts))
                file.close()
                correct = True
            elif accountnumber > 0 and accountnumber <= len(accounts):
                name = accounts[accountnumber - 1]['spotify_id']
                correct = True
            else:
                print("\n\n\nYOU ENTERED SOMETHING WRONG\n\n\n")
        except:
            print("\n\n\nYOU ENTERED SOMETHING WRONG\n\n\n")

    return name

def main():
    username = select_account()
    scope = 'user-read-currently-playing user-modify-playback-state'
    clientid = 'cb3d87487c3f45678e4f28c0f1787d59'
    clientsecret = '720cb763c5114ce581303e30846d962d'
    redirect_uri = 'http://google.com/'

    print("Choose which kind of server connection you want")
    print("1: Localhost")
    print("2: Remote server")
    print("3: No server conncetion")
    serverinput = input("-->: ")
    server = "http://82.75.204.165:8080/live_chords/"

    if serverinput == "2":
        server = "http://82.75.204.165:8080/live_chords/"
    elif serverinput == "3":
        server = "no_server"

    artist_old = ""
    artist = ""
    title_old = ""
    title = ""

    while True:
        title, artist, t0 = get_current_song(username, clientid, clientsecret, redirect_uri)
        artist = artist.replace(" ", "%20")
        title = title.replace(" ", "%20")

        if (artist != artist_old) or (title != title_old):
            print(("-" * 100 + "\n") * 3)
            datafile = file(artist, title, version, server)
            datafile.open_file()
            print_tabs(datafile)
            # datafile.close_file()
            artist_old = artist
            title_old = title

        else:
            time.sleep(5)


version = '2019-10-13'

if __name__ == "__main__":
    main()

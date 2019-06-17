import requests
from live_chords import seperate_lines

artist = "flogging-molly"
title = "the-powers-out"

searchurl = "https://genius.com/"+artist+"-"+title+"-lyrics"
r = requests.get(searchurl)
data = r.text
html_lines = seperate_lines(data)
on_lyrics = False
in_lyrics_class = False
lyrics = []
#loop over all lines in the html data and find when were in the lyrics class, the lyrics will be in the lyrics class within the sse tags. So if that is all true, add that line of html to the lyrics
for i, line in enumerate(html_lines):
    if line.strip()  == "<!--/sse-->" and in_lyrics_class:
        on_lyrics = False
    if on_lyrics:
        lyrics.append(line.replace("<br>","").replace("<p>","").replace("</p>","").replace("</a>","").strip()) #remove paragraph and breakline tags and ending annotation tag
    if line.strip() == "<!--sse-->" and in_lyrics_class:
        on_lyrics = True
    if line.strip() == "<div class=\"lyrics\">":
        in_lyrics_class = True

#no to scan the seperated lyrics for annotation tags, and remove them
annotationTag = False
i = 0
while i < len(lyrics):
    if lyrics[i][0:2] == "<a":
        for j in range(0,4):
            lyrics.pop(i)
        index = lyrics[i].find(">")
        lyrics[i] = lyrics[i][index+1:len(lyrics[i])]
        annotationTag = True
    else:
        i+=1


print(lyrics)
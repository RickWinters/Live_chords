import requests
from live_chords import seperate_lines

artist = "twarres"
title = "wer bisto"

searchurl = "https://songteksten.net/search.html?q="+title.replace(" ","+")+artist+"&type%5B%5D=title&type%5B%5D=artist"
html_lines = seperate_lines(requests.get(searchurl).text)

searchurl = "https://songteksten.net/search.html?q=wer+bisto&type%5B%5D=title&type%5B%5D=artist"
html_lines = seperate_lines(requests.get(searchurl).text)









searchurl = "https://songteksten.net/lyric/269/8521/twarres/wer-bisto.html"
r = requests.get(searchurl)
data = r.text
html_lines = seperate_lines(data)
on_lyrics = False
in_lyrics_class = False
lyrics = []
#loop over all lines in the html data and find when were in the lyrics class, the lyrics will be in the lyrics class within the sse tags. So if that is all true, add that line of html to the lyrics
for i, line in enumerate(html_lines):

    if "</div>" in line.strip() and on_lyrics:
        on_lyrics = False
    if on_lyrics:
        lyrics.append(line.replace("<br />",""))
    if "col-sm-7 content-left" in line.strip():
        on_lyrics = True


print(lyrics)
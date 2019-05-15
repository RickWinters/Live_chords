import json
import requests
from live_chords import seperate_lines
from bs4 import BeautifulSoup
from live_chords import Azlyrics



r = requests.get('http://localhost', 3306)

data = r.text
lines = seperate_lines(data)
print(data)
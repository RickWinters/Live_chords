import requests
import json

body = {}
body["name"] = "henk"
url = "localhost:8080"
r = requests.get(url)
data = r.text
print(data)

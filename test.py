from bot import Bot
ACCOUNT = "109502563"
PASSWORD = "H125920690"
import requests
import json
s = requests.Session()
url = Bot.URL
r = s.get(url)
#print(r.text)
print(r.cookies)
print(type(r.headers))

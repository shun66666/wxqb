# !/usr/bin/nev python
# -*-coding:utf8-*-

import requests,json


"""curl -U vpswote-country-US:6f4076-80e06b-e459f5-fe604d-ae99b4 -x premium.residential.rotating.proxyrack.net:10000 ip-api.com/json https://therecord.media/news/nation-state/"""
url = "https://therecord.media/news/nation-state/"
proxy =""
payload = {}
response = requests.request("GET", url, proxies=proxy, data=payload)
print(response.text)
errcode = json.loads(response.text)['meta']['errCode']
tableid = json.loads(response.text)['data']['tableId']
tablepath = json.loads(response.text)['data']['path']



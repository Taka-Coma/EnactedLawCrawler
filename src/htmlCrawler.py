# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from mojimoji import zen_to_han
from kanjize import kanji2int
import json
from glob import glob 
import os

import time 
from pprint import pprint

history_head = 'https://hourei.ndl.go.jp/#/detail?lawId='
processed = [f'{history_head}{path[path.rfind("/")+1:path.rfind("html")-1]}'
	for path in glob('../html/*')]

def main():
	urls = getURLList()

	for law in urls:
		law_id = law[law.find('=')+1:]

		html_path = f'../html/{law_id}.html'
		if os.path.exists(html_path):
			txt = getHTML('', html_path)
		else:
			txt = getHTML(urls[law], html_path)

		print(urls[law], law_id)

		time.sleep(1)



def getHTML(url, path):
	if os.path.exists(path):
		with open(path, 'r') as r:
			txt = ''.join(r.readlines())
	else:
		if url[:5] == 'http:':
			url = 'https:' + url[5:]
		res = requests.get(url)
		txt = res.text

		with open(path, 'w') as w:
			w.write(txt)

	return txt



def getURLList():
	endpoint = 'https://history.lawlod.net/sparql'

	query = '''
		select distinct ?id ?url
		where {
			?id a <https://history.lawlod.net/ontology/Law> ;
			    <https://history.lawlod.net/property/external> ?url.
			?url <http://www.w3.org/2000/01/rdf-schema#label> "衆議院_制定法律"@ja
			FILTER NOT EXISTS {
				?id <https://history.lawlod.net/property/eGovID> ?x 
			}
		}'''
	res = requests.get(endpoint, params={
		'defaul_graph': 'https://history.lawlod.net',
		'format': 'json',
		'query': query,
	})

	out = {r['id']['value']: r['url']['value']
		for r in res.json()['results']['bindings'] 
			if r['id']['value'] not in processed}

	return out


if __name__ == "__main__":
    main()


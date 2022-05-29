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
processed = [f'{history_head}{path[path.rfind("/")+1:path.rfind("json")-1]}'
	for path in glob('../json/*')]

def main():
	urls = getURLList()

	for law in urls:
		law_id = law[law.find('=')+1:]

		html_path = f'../html/{law_id}.html'
		if os.path.exists(html_path):
			txt = getHTML('', html_path)
		else:
			txt = getHTML(laws[law], html_path)

		print(urls[law], law_id)

		data = parseHTML(txt)

		if data == {}:
			continue 

		with open(f'../json/{law_id}.json', 'w') as w:
			json.dump(data, w)

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






title_head = '　　◎'
article_title_head = '　（'


def parseHTML(txt):
	soup = BeautifulSoup(txt)

	out = {}
	tmp_article_title = ''
	art_num = 0
	para_num = 1
	for p in soup.select('#mainlayout > .hj1pj'):
		txt = p.string
		if txt is None:
			continue

		if txt[:len(title_head)] == title_head:
			out['title'] = txt[len(title_head):].strip()

		elif txt[:len(article_title_head)] == article_title_head:
			tmp_article_title = txt.strip()

		elif txt[0] == '第':
			art_num += 1
			paragraph_txt = txt[txt.find('条')+1:].strip()
			out[art_num] = {
				'paragraphs': {1 : [paragraph_txt]}	
			}
			if tmp_article_title:
				out[art_num]['title'] = tmp_article_title
				tmp_article_title = ''
			para_num = 1

		elif txt == '　　　附　則':
			art_num = 9999
			out[art_num] = {
				'head': txt.strip(),
				'paragraphs': {1: []}
			}
			para_num = 1

		elif txt[0] == '　':
			if art_num == 0:
				art_num = 1
				out[art_num] = {'paragraphs': {1: [txt.strip()]}}
			else:
				out[art_num]['paragraphs'][para_num].append( txt.strip() )

		elif txt[0] == '（':
			out['signature'] = txt.strip()

		else:
			if art_num == 0:
				continue

			tmp_para_num = zen_to_han(txt[:txt.find('　')])
			
			try:
				num_int = int(tmp_para_num)
				out[art_num]['paragraphs'][num_int] = [txt[txt.find('　')+1:]]
				para_num = num_int
			except:
				out[art_num]['paragraphs'][para_num].append(txt[txt.find('　')+1:])

	return out


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


# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from mojimoji import zen_to_han

from pprint import pprint


processed = []
with open('./processed.txt', 'r') as r:
	for line in r:
		processed.append(line.strip())

headers = {
	'User-Agent': 'Mozilla/5.0'
}

def main():
	urls = getURLList()

	for law in urls:
		data = parseHTML(urls[law])

		print(urls[law])
		pprint(data)

		break


title_head = '　　◎'
article_title_head = '　（'


def parseHTML(url):
	if url[:5] == 'http:':
		url = 'https:' + url[5:]
	res = requests.get(url, headers=headers)
	soup = BeautifulSoup(res.text)

	out = {}
	tmp_article_title = ''
	art_num = 0
	for p in soup.find(id='mainlayout').find_all('p'):
		txt = p.string

		if txt[:len(title_head)] == title_head:
			out['title'] = txt[len(title_head):].strip()

		elif txt[:len(article_title_head)] == article_title_head:
			tmp_article_title = txt.strip()

		elif txt[0] == '第':
			art_num += 1
			paragraph_txt = txt[txt.find('条')+1:].strip()
			out[art_num] = {
				'head': paragraph_txt,
				'texts': []
			}
			if tmp_article_title:
				out[art_num]['title'] = tmp_article_title
				tmp_article_title = ''

		elif txt == '　　　附　則':
			art_num = 9999
			out[art_num] = {
				'head': txt.strip(),
				'paragraphs': {}
			}

		elif txt[0] == '　':
			out[art_num]['texts'].append(txt.strip())

		else:
			para_num = zen_to_han(txt[:txt.find('　')])
			try:
				num_int = int(para_num)
				out[art_num]['paragraph'][num_int] = txt[txt.find('　')+1:]
			except:
				print(f'|||| [s]{para_num}[e]')
				print('||||', txt)

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

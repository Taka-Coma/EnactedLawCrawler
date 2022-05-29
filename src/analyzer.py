# -*- coding: utf-8 -*-

import json
import requests
from bs4 import BeautifulSoup
import os

def main():
	base_path = '../json/'

	### 道路運送車両法の一部を改正する法律（令和元年5月24日法律第14号）
	target = '0000148470'

	with open(f'{base_path}{target}.json', 'w') as w:
		json.dump(data, w)

	print(data)


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


title_head = '◎'
article_title_head = '　（'


def parseHTML(txt):
	soup = BeautifulSoup(txt)

	out = {}
	tmp_article_title = ''
	art_num = 0
	para_num = 1
	for p in soup.select('#mainlayout > p'):
		txt = p.string.replace('\n', '')

		if txt is None:
			continue

		if txt.find(title_head) > -1:
			out['title'] = txt[txt.find(title_head)+1:].strip()

		elif txt[:len(article_title_head)] == article_title_head:
			tmp_article_title = txt.strip()

		elif txt.find('第') == 0:
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
			art_num = 1000
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






if __name__ == "__main__":
    main()

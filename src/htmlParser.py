# -*- coding: utf-8 -*-

import json
import requests
from bs4 import BeautifulSoup
import os
from glob import glob
from mojimoji import zen_to_han
from kanjize import kanji2int

def main():
	base_path = '../json/'

	for path in glob('../html/*'):
		target = path[path.rfind("/")+1:path.rfind("html")-1]

		print(target)

		with open(path, 'r') as r:
			txt = ''.join(r.readlines())

		if os.path.exists(f'{base_path}{target}.json'):
			print('\tpassed')
			continue

		data = parseHTML(txt)

		with open(f'{base_path}{target}.json', 'w') as w:
			json.dump(data, w)


title_head = '◎'
article_title_head = '　（'

def parseHTML(txt):
	soup = BeautifulSoup(txt)

	out = {}
	tmp_article_title = ''
	art_num = 0
	para_num = 1
	for p in soup.select('#mainlayout > p'):
		txt = p.string

		if txt is None:
			continue

		txt = txt.replace('\n', '')

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

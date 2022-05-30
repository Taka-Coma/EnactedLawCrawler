# -*- coding: utf-8 -*-

import json
import re
from glob import glob
import os
from collections import Counter
import math

def main():
	save_path = '../workspace/changeWordWeight.json'

	if os.path.exists(save_path):
		with open(save_path, 'r') as r:
			data = json.load(r)
	else:
		changeWords = getAllWordChanges()

		data = {}
		for target in changeWords:
			tmp = calcTermWeight(changeWords, target)
			if len(tmp) == 0:
				continue
			data[target] = tmp

		with open(save_path, 'w') as w:
			json.dump(data, w)




### 道路運送車両法の一部を改正する法律（令和元年法律第14号）
def calcTermWeight(changeWords, target='0000148470'):
	n_doc = len(changeWords)

	df_src = Counter([rec['src_term']
		for law in changeWords
		for rec in changeWords[law]
		])

	df_dst = Counter([term
		for law in changeWords
		for rec in changeWords[law]
		for term in rec['dst_term']
		])

	terms = changeWords[target]

	out = []
	for term_dict in terms:
		tfidf_src = term_dict['relative_count']*(math.log(n_doc/df_src[term_dict['src_term']])+1)

		for term_dst in term_dict['dst_term']:
			tfidf_dst = term_dict['relative_count']*(math.log(n_doc/df_dst[term_dst])+1)

			#print(f'{tfidf_src:.3f}: {term_dict["src_term"]} - {tfidf_dst:.3f}: {term_dst}')
			out.append({'src': {
				'term': term_dict["src_term"],
				'tfidf': tfidf_src 
				}, 'dst': {
				'term': term_dst,
				'tfidf': tfidf_dst
				}})
	return out


def getAllWordChanges():
	save_path = '../workspace/changeWords.json'

	if os.path.exists(save_path):
		with open(save_path, 'r') as r:
			data = json.load(r)
	else:
		data = {}
		for path in glob('../json/*.json'):
			target = path[path.rfind('/')+1:path.find('.json')]
			tmp = extractWordChange(target)
			if len(tmp) == 0:
				continue
			data[target] = tmp

		with open(save_path, 'w') as w:
			json.dump(data, w)

	return data


### 道路運送車両法の一部を改正する法律（令和元年5月24日法律第14号）
#target = '0000148470'
def extractWordChange(target='0000148470'):
	base_path = '../json/'

	replace_pattern = re.compile('「(を削り、)?(.+?)」を「(.+?)」に')
	front_symbol_pattern = re.compile('^[は|の|を|が|に|、|」|「|（|）]')
	end_symbol_pattern = re.compile('[は|の|を|が|に|、|」|「|（|）]$')

	with open(f'{base_path}{target}.json', 'r') as r:
		data = json.load(r)

	replaces = {}

	articles = data['articles']
	for art in articles:
#		print(art)

		paragraphs = articles[art]['paragraphs']
		for para in paragraphs:
			for i, sent in enumerate(paragraphs[para]):
				if sent.find('改正する') > -1:
					continue

				### 「改め」パターン
				matches = list(replace_pattern.findall(sent))

				if len(matches) == 0:
					continue

				for match in matches: 
					if match[1].find('条') > -1 or match[1].find('項') > -1 or match[1].find('号') > -1:
						continue
					#print([symbol_pattern.sub('', m) for m in match])

					head = end_symbol_pattern.sub('', front_symbol_pattern.sub('', match[1]))
					tail = end_symbol_pattern.sub('', front_symbol_pattern.sub('', match[2]))

					if len(head) == 0 or len(tail) == 0:
						continue

					min_len = len(head)
					if len(tail) < min_len:
						max_len = min_len
						min_len = len(tail)
					else:
						max_len = len(tail)

					if max_len / min_len > 2:
						continue

					if head not in replaces:
						replaces[head] = []

					replaces[head].append(tail)

	total_count = sum([len(replaces[src]) for src in replaces])
	out = [{'count': len(replaces[src]), 
		'relative_count': len(replaces[src])/total_count,
		'src_term': src,
		'dst_term': replaces[src]}
		for src in replaces]

	return out


if __name__ == "__main__":
	main()

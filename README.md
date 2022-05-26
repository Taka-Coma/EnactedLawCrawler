# 制定法律クローラ

- 目的：衆議院のページに掲載されている制定法律の本文を抽出し構造化
	- https://www.shugiin.go.jp/internet/itdb_housei.nsf/html/housei/kaiji208_l.htm

- `src/crawler.py`
	1. [法令沿革 LOD](https://www.lawlod.net/historylod/) から制定法律の URL を取得
		- SPARQL Endpoint > https://history.lawlod.net/sparql/
	2. 取得した URL から制定法律のページの HTML ファイルを取得
	3. 取得した HTML ファイルを解析し，構造化

- To do
	- 別表の処理：現状，表は無視している．　

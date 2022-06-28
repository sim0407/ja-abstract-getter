
from optparse import check_builtin
from posixpath import dirname
from re import search
from turtle import title
from urllib import response


class AllPapersProcessor:
    def __init__(self) -> None:
        self.search_words = ''
        self.papers = []
        self.PMIDs = []


    def input_search_words(self):
        self.search_words = input('検索キーワードを入力してください＞')
    
    #search_wordsを使って、PMIDsを作る
    def search(self):
        import requests
        import xml.etree.ElementTree as et
        # 検索
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        term = self.search_words
        payload = {
            "db":"pubmed",
            "term":term,
            "usehistory":"y"
        }

        ret = requests.get(url, params=payload)
        xml = ret.text.encode("utf-8")
        root = et.fromstring(xml)
        print(root)
        for id in root.find('IdList').findall('Id'):
            print(id.text)
            self.PMIDs.append(id.text)


    def process(self):
        for PMID in self.PMIDs:
            self.papers.append(OnePaperInformation(PMID))
        for paper in self.papers:
            paper.convert_PMID_to_URL()
            paper.get_paper_info()
            paper.translate_en_to_ja()
            paper.test()

    #One.outputを使って情報を取り出して、それをCSVに書き出す
    def save(self):
        import csv
        import os
        dir_name = os.getcwd()
        all_papers_info_list = []
        for paper in self.papers:
            all_papers_info_list.append(paper.output())
        with open(dir_name+'/'+self.search_words+'.csv', 'w', encoding='utf8') as f:
            writer = csv.writer(f, lineterminator= '\n')
            writer.writerows(all_papers_info_list)
    


class OnePaperInformation:
    def __init__(self, PMID) -> None:
        self.URL = ''
        self.PMID = PMID
        self.response = ''

        self.title = ''
        self.autors = ''
        self.journal = ''
        self.date = ''
        self.en_abstract = ''
        self.ja_abstract = ''
    
    def convert_PMID_to_URL(self):
        self.URL = 'https://pubmed.ncbi.nlm.nih.gov/' + self.PMID + '/'
        

    def HTTP_request(self):
        import requests
        self.response = requests.get(self.URL)

    def extract_paper_info(self):
        import requests
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(self.response.text, 'html.parser')
        self.title = soup.select('div#short-view-heading h1.heading-title')[0].get_text().strip()
        self.autors = soup.select('div#short-view-heading span.authors-list')[0].get_text().strip()
        self.journal = soup.select('div#short-view-heading span.citation-journal')[0].get_text().strip()
        self.date = soup.select('div#short-view-heading span.date')[0].get_text().strip()
        self.en_abstract = soup.select('div#enc-abstract')[0].get_text().strip()
        #TODO 必要な要素の確認
    
    def get_paper_info(self):
        self.HTTP_request()
        self.extract_paper_info()


    def translate_en_to_ja(self):
        import requests
        API_KEY = ''#こちらにご自分のAPI keyを入力してください
        text = self.en_abstract
        source_lang = 'EN'
        target_lang = 'JA'
        # パラメータの指定
        params = {
                    'auth_key' : API_KEY,
                    'text' : text,
                    'source_lang' : source_lang, # 翻訳対象の言語
                    "target_lang": target_lang  # 翻訳後の言語
                }

        # リクエストを投げる
        request = requests.post("https://api-free.deepl.com/v2/translate", data=params) # URIは有償版, 無償版で異なるため要注意
        result = request.json()
        self.ja_abstract = result['translations'][0]['text']
    
    def output(self):
        return [self.title, self.autors, self.journal, self.date, self.en_abstract, self.ja_abstract]
    
    def test(self):
        print(self.title)
        print(self.en_abstract)
        print(self.ja_abstract)
        

def main():
    all_papers = AllPapersProcessor()
    all_papers.input_search_words()
    all_papers.search()
    all_papers.process()
    all_papers.save()


main()





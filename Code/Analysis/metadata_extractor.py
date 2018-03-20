from bs4 import BeautifulSoup
import zipfile
import tempfile
import shutil
import os
# "/run/media/mfajet/Data/projects/Web-Page-Archiving-and-Content-Analysis-1.0/Code/watapp/outdir/files/15196120301161_theverge.com/amazon-echo-google-home-nsa-voice-surveillance.html"

class MetadataExtractor:
    """Simple metadata extractor"""
    def __init__(self):
        self.data = {}
        self.article = None

    def save_first(self, methods, prop):
        for method in methods:
            try:
                val = method()
                if val:
                    self.data[prop] = val
                    break
            except Exception as e:
                continue

    def get_title(self):
        title_methods=[
        lambda: self.article.find("meta",  property="og:title")["content"],
        lambda: self.article.title.string,
        lambda: self.article.find("meta", attrs={'name':'twitter:title'} ).get("content", None),
        lambda: self.article.find("meta", attrs={'name':'sailthru.title'}).get("content", None),
        lambda: self.article.find("meta", attrs={'name':'dc.title'}).get("content", None),
        lambda: self.article.find("meta", attrs={'name':'DC.title'}).get("content", None),
        lambda: self.article.find("meta", attrs={'name':'title'}).get("content", None)
        ]
        self.save_first(title_methods,"title")
    def get_author(self):
        author_methods=[
            lambda: self.article.find("meta",  property="author")["content"],
            lambda: self.article.find("meta",  property="self.article:author")["content"],
            lambda: self.article.find("meta", attrs={'name':'sailthru.author'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'author'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'dc.creator'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'DC.creator'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'dc.contributor'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'DC.contributor'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'twitter:creator'} ).get("content", None)
        ]
        self.save_first(author_methods,"author")

    def get_date(self):
        date_methods=[
            lambda: self.article.find("meta",  property="date")["content"],
            lambda: self.article.find("meta",  property="self.article:published_time")["content"],
            lambda: self.article.find("meta",  property="self.article:modified_time")["content"],
            lambda: self.article.find("meta", attrs={'name':'sailthru.date'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'dc.date'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'dc.date.issued'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'DC.date'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'DC.date.issued'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'date'}).get("content", None)
        ]
        self.save_first(date_methods,"date")

    def get_header(self):
        header_methods=[
            lambda: self.article.find("meta", attrs={'name':'description'}).get("content", None),
            lambda: self.article.find("meta",  property="og:description")["content"],
            lambda: self.article.find("meta",  property="description")["content"],
            lambda: self.article.find("meta", attrs={'name':'twitter:description'} ).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'sailthru.description'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'dc.description'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'DC.description'}).get("content", None)
        ]
        self.save_first(header_methods,"header")

    def get_publisher(self):
        publisher_methods=[
            lambda: self.article.find("meta",  property="self.article:publisher")["content"],
            lambda: self.article.find("meta",  property="publisher")["content"],
            lambda: self.article.find("meta",  property="og:site_name")["content"],
            lambda: self.article.find("meta", attrs={'name':'twitter:site'} ).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'sailthru.description'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'dc.publisher'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'DC.publisher'}).get("content", None)
        ]
        self.save_first(publisher_methods,"header")

    def extract_data_from_html(self, file_name):
        with open(file_name) as fp:
            self.article = BeautifulSoup(fp, 'html.parser')
        self.get_date()
        self.get_title()
        self.get_author()
        self.get_publisher()
        self.get_header()
        return self.data

    def extract_data_from_wat(self,wat_file):
        dirpath = os.path.join(tempfile.mkdtemp(),"extraction")

        archive = zipfile.ZipFile(wat_file)
        archive.extract("wat_link.txt", dirpath)
        with open(os.path.join(dirpath,"wat_link.txt")) as f:
            file = f.readline()
        archive.extract(file,dirpath)
        data= self.extract_data_from_html(os.path.join(dirpath,file))
        shutil.rmtree(dirpath)
        return data

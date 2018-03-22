from bs4 import BeautifulSoup
import zipfile
import tempfile
import shutil
import os
import re
import json
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
                    self.data[prop] = val.encode('utf-8')
                    break
                else:
                    self.data[prop]= None
            except Exception as e:
                continue

    def get_title(self):
        title_methods=[
            lambda: json.loads(self.article.find("script", attrs={'type':'application/ld+json'}).contents[0])["headline"],
            lambda: self.article.find("meta",  property="og:title")["content"],
            lambda: self.article.title.string,
            lambda: self.article.find("meta", attrs={'name':'twitter:title'} ).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'sailthru.title'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'dc.title'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'DC.title'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'title'}).get("content", None),
            lambda: self.article.find("meta",  property="og:title")["content"],
            lambda: self.article.find("meta", attrs={'name':'twitter:title'} ).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'sailthru.title'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'dc.title'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'DC.title'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'title'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'mrc__share_title'} ).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'mrc__share_title'} ).get("content", None),
        ]
        self.save_first(title_methods,"title")

    def get_author(self):
        author_methods=[
            lambda: json.loads(self.article.find("script", attrs={'type':'application/ld+json'}).contents[0])["author"]["name"],
            lambda: self.article.find("meta", attrs={'name':'author'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'Author'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'Author'}).get("value", None),
            lambda: self.article.find("meta",  property="author")["content"],
            lambda: self.article.find("meta",  property="article:author")["content"],
            lambda: self.article.find("meta", attrs={'name':'sailthru.author'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'dc.creator'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'DC.creator'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'dc.contributor'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'DC.contributor'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'twitter:creator'} ).get("content", None),
            lambda: self.article.find("meta", property="author")["value"],
            lambda: self.article.find("meta", property="article:author")["value"],
            lambda: self.article.find("meta", attrs={'name':'sailthru.author'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'author'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'dc.creator'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'DC.creator'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'dc.contributor'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'DC.contributor'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'twitter:creator'} ).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'mediator_author'} ).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'mediator_author'} ).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'analyticsAttributes.author'} ).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'analyticsAttributes.author'} ).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'DCSext.author'} ).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'DCSext.author'} ).get("content", None),
            lambda: json.loads(self.article.find("script", attrs={'type':'application/ld+json'}).contents[0])["creator"][0],
            lambda: json.loads(self.article.find("script", attrs={'type':'application/ld+json'}).contents[0])["creator"],
            lambda: json.loads(self.article.find("script", attrs={'type':'application/ld+json'}).contents[0])["author"],
        ]
        self.save_first(author_methods,"author")

    def get_published_date(self):
        date_methods=[
            lambda: self.article.find("meta",  property="date")["content"],
            lambda: self.article.find("meta",  property="article:published_time")["content"],
            lambda: self.article.find("meta",  property="article:published")["content"],
            lambda: self.article.find("meta", attrs={'name':'sailthru.date'}).get("content", None),
            lambda: self.article.find("meta", attrs={'itemprop':'DCSext.articleFirstPublished'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'dc.date'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'dc.date.issued'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'DC.date'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'DC.date.issued'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'date'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'ptime'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'pdate'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'DISPLAYDATE'}).get("content", None),
            lambda: self.article.find("meta",  property="date")["value"],
            lambda: self.article.find("meta",  property="article:published_time")["value"],
            lambda: self.article.find("meta",  property="article:published")["value"],
            lambda: self.article.find("meta", attrs={'name':'sailthru.date'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'dc.date'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'dc.date.issued'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'DC.date'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'DC.date.issued'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'date'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'ptime'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'pdate'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'DISPLAYDATE'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'published_time_telegram'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'published_time_telegram'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'mediator_published_time'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'mediator_published_time'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'publish_date'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'publish_date'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'pubdate'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'pubdate'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'analyticsAttributes.articleDate'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'analyticsAttributes.articleDate'}).get("value", None),
            lambda: self.article.find("meta", attrs={'itemprop':'datePublished'}).get("content", None),
            lambda: self.article.find("meta", attrs={'itemprop':'datePublished'}).get("value", None),
            lambda: self.article.find("meta", attrs={'itemprop':'DCSext.articleFirstPublished'}).get("value", None),
            lambda: json.loads(self.article.find("script", attrs={'type':'application/ld+json'}).contents[0])["datePublished"],
        ]
        self.save_first(date_methods,"publishedDate")

    def get_modified_date(self):
        date_methods=[
            lambda: self.article.find("meta",  property="article:modified_time")["content"],
            lambda: self.article.find("meta",  property="article:modified")["content"],
            lambda: self.article.find("meta", attrs={'name':'utime'}).get("content", None),
            lambda: self.article.find("meta",  property="article:modified_time")["value"],
            lambda: self.article.find("meta",  property="article:modified")["value"],
            lambda: self.article.find("meta", attrs={'name':'utime'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'lastmod'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'lastmod'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'last-modified'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'last-modified'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'modified'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'modified'}).get("value", None),
            lambda: self.article.find("meta", attrs={'itemprop':'dateModified'}).get("content", None),
            lambda: self.article.find("meta", attrs={'itemprop':'dateModified'}).get("value", None),
            lambda: self.article.find("meta", attrs={'itemprop':'REVISION_DATE'}).get("content", None),
            lambda: self.article.find("meta", attrs={'itemprop':'REVISION_DATE'}).get("value", None),
            lambda: json.loads(self.article.find("script", attrs={'type':'application/ld+json'}).contents[0])["dateModified"],
        ]
        self.save_first(date_methods,"modifiedDate")

    def get_created_date(self):
        date_methods=[
            lambda: self.article.find("meta", attrs={'itemprop':'dateCreated'}).get("content", None),
            lambda: self.article.find("meta", attrs={'itemprop':'dateCreated'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'created'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'created'}).get("value", None),
            lambda: json.loads(self.article.find("script", attrs={'type':'application/ld+json'}).contents[0])["dateCreated"],
        ]
        self.save_first(date_methods,"createdDate")

    def get_header(self):
        header_methods=[
            lambda: self.article.find("meta", attrs={'name':'description'}).get("content", None),
            lambda: self.article.find("meta",  property="og:description")["content"],
            lambda: self.article.find("meta",  property="description")["content"],
            lambda: self.article.find("meta", attrs={'name':'twitter:description'} ).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'sailthru.description'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'dc.description'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'DC.description'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'description'}).get("value", None),
            lambda: self.article.find("meta",  property="og:description")["value"],
            lambda: self.article.find("meta",  property="description")["value"],
            lambda: self.article.find("meta", attrs={'name':'twitter:description'} ).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'sailthru.description'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'dc.description'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'DC.description'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'mrc__share_description'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'mrc__share_description'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'pin:description'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'pin:description'}).get("value", None),
            lambda: json.loads(self.article.find("script", attrs={'type':'application/ld+json'}).contents[0])["description"],

        ]
        self.save_first(header_methods,"header")

    def get_publisher(self):
        publisher_methods=[
            lambda: json.loads(self.article.find("script", attrs={'type':'application/ld+json'}).contents[0])["publisher"]["name"],
            lambda: self.article.find("meta",  property="og:site_name")["content"],
            lambda: self.article.find("meta", attrs={'name':'cre'} ).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'cre'} ).get("value", None),
            lambda: self.article.find("meta",  property="article:publisher")["content"],
            lambda: self.article.find("meta",  property="publisher")["content"],
            lambda: re.sub('@', '', self.article.find("meta", attrs={'name':'twitter:site'} ).get("content", None)),
            lambda: self.article.find("meta", attrs={'name':'sailthru.description'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'dc.publisher'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'DC.publisher'}).get("content", None),
            lambda: self.article.find("meta",  property="article:publisher")["value"],
            lambda: self.article.find("meta",  property="publisher")["value"],
            lambda: self.article.find("meta",  property="og:site_name")["value"],
            lambda: self.article.find("meta", attrs={'name':'twitter:site'} ).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'sailthru.description'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'dc.publisher'}).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'DC.publisher'}).get("value", None),

        ]
        self.save_first(publisher_methods,"publisher")

    def get_publisher_origin(self):
        publisher_origin_methods=[
            lambda: self.article.find("meta", attrs={'name':'sailthru.location'}).get("content", None),

        ]
        self.save_first(publisher_origin_methods,"publisherOrigin")

    def get_language(self):
        language_methods=[
            lambda: self.article.find("meta",  property="og:locale")["content"],
            lambda: self.article.find("meta", attrs={'name':'DC.language'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'language'}).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'lang'}).get("content", None),
            lambda: self.article.find("meta",  property="language")["content"],
            lambda: self.article.find("meta",  property="lang")["content"],

        ]
        self.save_first(language_methods,"language")

    def get_url(self):
        url_methods=[
            lambda: self.article.find("meta",  property="og:url")["content"],
            lambda: self.article.find("meta", attrs={'name':'twitter:url'} ).get("content", None),
            lambda: self.article.find("meta",  property="og:url")["value"],
            lambda: self.article.find("meta", attrs={'name':'twitter:url'} ).get("value", None),
            lambda: self.article.find("meta", attrs={'name':'analyticsAttributes.canonicalUrl'} ).get("content", None),
            lambda: self.article.find("meta", attrs={'name':'analyticsAttributes.canonicalUrl'} ).get("content", None),
            lambda: json.loads(self.article.find("script", attrs={'type':'application/ld+json'}).contents[0])["url"],
            lambda: json.loads(self.article.find("script", attrs={'type':'application/ld+json'}).contents[0])["mainEntityOfPage"]["@id"],
            lambda: json.loads(self.article.find("script", attrs={'type':'application/ld+json'}).contents[0])["mainEntityOfPage"],
            lambda: self.article.find("link", attrs={'rel':'amphtml'} ).get("href", None),
            lambda: self.article.find("link", attrs={'rel':'canonical'} ).get("href", None),

        ]
        self.save_first(url_methods,"url")


    def extract_data_from_html(self, file_name):
        self.data={}
        with open(file_name) as fp:
            self.article = BeautifulSoup(fp, 'html.parser')
        self.get_published_date()
        self.get_modified_date()
        self.get_created_date()
        self.get_title()
        self.get_author()
        self.get_publisher()
        self.get_header()
        self.get_publisher_origin()
        self.get_language()
        self.get_url()
        return self.data

    def extract_data_from_wat(self,wat_file):
        self.data={}
        dirpath = os.path.join(tempfile.mkdtemp(),"extraction")

        archive = zipfile.ZipFile(wat_file)
        archive.extract("wat_link.txt", dirpath)
        with open(os.path.join(dirpath,"wat_link.txt")) as f:
            file = f.readline()
        archive.extract(file,dirpath)
        data= self.extract_data_from_html(os.path.join(dirpath,file))
        shutil.rmtree(dirpath)
        return data

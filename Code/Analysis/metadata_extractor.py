from bs4 import BeautifulSoup

with open("/run/media/mfajet/Data/projects/Web-Page-Archiving-and-Content-Analysis-1.0/Code/watapp/outdir/files/15196120301161_theverge.com/amazon-echo-google-home-nsa-voice-surveillance.html") as fp:
    article = BeautifulSoup(fp, 'html.parser')

data = {}

def save_first(methods, prop):
    for method in methods:
        try:
            val = method()
            if val:
                data[prop] = val
                break
        except Exception as e:
            continue

title_methods=[
lambda: article.find("meta",  property="og:title")["content"],
lambda: article.title.string,
lambda: article.find("meta", attrs={'name':'twitter:title'} ).get("content", None),
lambda: article.find("meta", attrs={'name':'sailthru.title'}).get("content", None),
lambda: article.find("meta", attrs={'name':'dc.title'}).get("content", None),
lambda: article.find("meta", attrs={'name':'DC.title'}).get("content", None),
lambda: article.find("meta", attrs={'name':'title'}).get("content", None)
]
save_first(title_methods,"title")

author_methods=[
    lambda: article.find("meta",  property="author")["content"],
    lambda: article.find("meta",  property="article:author")["content"],
    lambda: article.find("meta", attrs={'name':'sailthru.author'}).get("content", None),
    lambda: article.find("meta", attrs={'name':'author'}).get("content", None),
    lambda: article.find("meta", attrs={'name':'dc.creator'}).get("content", None),
    lambda: article.find("meta", attrs={'name':'DC.creator'}).get("content", None),
    lambda: article.find("meta", attrs={'name':'dc.contributor'}).get("content", None),
    lambda: article.find("meta", attrs={'name':'DC.contributor'}).get("content", None),
    lambda: article.find("meta", attrs={'name':'twitter:creator'} ).get("content", None)
]
save_first(author_methods,"author")

date_methods=[
    lambda: article.find("meta",  property="date")["content"],
    lambda: article.find("meta",  property="article:published_time")["content"],
    lambda: article.find("meta",  property="article:modified_time")["content"],
    lambda: article.find("meta", attrs={'name':'sailthru.date'}).get("content", None),
    lambda: article.find("meta", attrs={'name':'dc.date'}).get("content", None),
    lambda: article.find("meta", attrs={'name':'dc.date.issued'}).get("content", None),
    lambda: article.find("meta", attrs={'name':'DC.date'}).get("content", None),
    lambda: article.find("meta", attrs={'name':'DC.date.issued'}).get("content", None),
    lambda: article.find("meta", attrs={'name':'date'}).get("content", None)
]
save_first(date_methods,"date")

header_methods=[
    lambda: article.find("meta", attrs={'name':'description'}).get("content", None),
    lambda: article.find("meta",  property="og:description")["content"],
    lambda: article.find("meta",  property="description")["content"],
    lambda: article.find("meta", attrs={'name':'twitter:description'} ).get("content", None),
    lambda: article.find("meta", attrs={'name':'sailthru.description'}).get("content", None),
    lambda: article.find("meta", attrs={'name':'dc.description'}).get("content", None),
    lambda: article.find("meta", attrs={'name':'DC.description'}).get("content", None)
]
save_first(header_methods,"header")

publisher_methods=[
    lambda: article.find("meta",  property="article:publisher")["content"],
    lambda: article.find("meta",  property="publisher")["content"],
    lambda: article.find("meta",  property="og:site_name")["content"],
    lambda: article.find("meta", attrs={'name':'twitter:site'} ).get("content", None),
    lambda: article.find("meta", attrs={'name':'sailthru.description'}).get("content", None),
    lambda: article.find("meta", attrs={'name':'dc.publisher'}).get("content", None),
    lambda: article.find("meta", attrs={'name':'DC.publisher'}).get("content", None)
]
save_first(header_methods,"header")

print data

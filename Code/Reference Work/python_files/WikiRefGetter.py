import pandas as pd
from bs4 import BeautifulSoup
import urllib.request
import urllib.error
import os
from langdetect import detect
import time
import datetime
import http.client
from urllib.parse import urlparse
import subprocess

class Link:
    def __init__(self, title = "", publisher = "", links = None):
        self.title = title
        self.publisher = publisher
        self.links = links if links is not None else []

class WikiRefGetter:

    def __init__(self, txt_file, seen_links = None):
        self.txt_file = txt_file
        if seen_links is None:
            self.seen_links = dict()
        else:
            self.seen_links = seen_links
        self.load_seen_links(txt_file)

    #expecting only wiki links
    def html_from_link(self, url):
        try:
            with urllib.request.urlopen(url) as response:
                html = response.read()
        except:
            print("bad wiki link " + url)
        return html

    def english(self, dict):
        list = [(k, v) for (k, v) in dict.items()]
        to_del = []
        for k, v in list:
            try:
                lang = detect(v.title.strip())
                if (lang == 'ru' or lang == 'uk'):
                    to_del.append(k)
            except:
                print("bad title")
        for k in to_del:
            del dict[k]
        return dict

    #make sure http response is good, remove previously seen links
    def clean_sources(self, dict):
        list = dict.keys()
        to_del = []
        for k in list:
            deleted = False
            if k.strip() in self.seen_links or 'kyivpost' in k:
                print("seen/kyiv skipping " + k)
                to_del.append(k)
                deleted = True
            parsed = urlparse(k)
            # host = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
            if (not deleted):
                try:
                    conn = http.client.HTTPConnection(parsed.hostname)
                    conn.request("HEAD", parsed.path)
                    stat = int(conn.getresponse().status)
                    if (stat >= 400):
                        to_del.append(k)
                        print(str(stat) + " deleting " + k)
                    else:
                        continue
                except:
                    to_del.append(k)
                    print("error, deleting " + k)
        for l in to_del:
            del dict[l]
        return dict

#sudo wget -np -N -k -p -nd -nH -H -E --no-check-certificate -e robots=off -U 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4' -P ~/Desktop https://www.gnu.org

    def wiki_soup(self, html):
        sources = {}
        soup = BeautifulSoup(html, 'html.parser')

        for li in soup.find_all("ol", {"class": "references"}):
            for cit_news in li.find_all("cite", {"class": 'citation news'}):
                i = 0
                l = Link()
                for e_text in cit_news.find_all("a", {"class": 'external text'}):
                    i = i + 1
                    if (i == 1):
                        l.title = str(e_text.string)[1:-1] if (str(e_text.string).startswith('"') and str(
                            e_text.string).endswith('"')) \
                                                              or (str(e_text.string).startswith('\'') and str(
                            e_text.string).endswith('\'')) \
                            else str(e_text.string)
                        l.links.append(str(e_text['href']))
                        l.publisher = cit_news.find("i").text if cit_news.find("i") \
                            else urlparse(str(e_text['href'])).hostname
                    else:
                        l.links.append(str(e_text['href']))
                        if 'wayback' in l.publisher or 'archive' in l.publisher:
                            l.publisher = urlparse(str(e_text['href'])).hostname
                try:
                    sources[l.links[0]] = l
                except:
                    print(str(e_text))
            for cit_web in li.find_all("cite", {"class": 'citation web'}):
                i = 0
                l = Link()
                for e_text in cit_web.find_all("a", {"class": 'external text'}):
                    i = i + 1
                    if (i == 1):
                        l.title = str(e_text.string)[1:-1] if (str(e_text.string).startswith('"') and str(
                            e_text.string).endswith('"')) \
                                                              or (str(e_text.string).startswith('\'') and str(
                            e_text.string).endswith('\'')) \
                            else str(e_text.string)
                        l.links.append(str(e_text['href']))
                        l.publisher = cit_web.find("i").text if cit_web.find("i") \
                            else urlparse(str(e_text['href'])).hostname
                    else:
                        l.links.append(str(e_text['href']))
                        if 'wayback' in l.publisher or 'archive' in l.publisher:
                            l.publisher = urlparse(str(e_text['href'])).hostname
                try:
                    sources[l.links[0]] = l
                except:
                    print(str(e_text))

        return self.clean_sources(self.english(sources))

    def fetch_html(self, l, path):
        link = l.links[0]
        if (len(l.links) > 1):
            if('wayback' in l.links[0] or 'archive' in l.links[0]):
                link = l.links[1]
                temp = l.links[0]
                l.links[0] = l.links[1]
                l.links[1] = temp
        cmd = "wget -np -N -k -p -nd -nH -H -E -R mpg,mpeg,mp3,mp4,wav,au,audio.aspx --no-check-certificate -e robots=off -U 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4' -P " + path + " " + "\"" + link.strip() + "\""
        os.system(cmd)
        #make sure wget worked
        if (os.path.exists(path)):
            return True
        else:
            return False
        # for f in os.listdir(path):
        #     if 'html' in f:
        #         os.rename(path + "/" + f, path + "/" + "index.html")

    def make_row(self, filename, link):

        newRow = pd.DataFrame(columns = ['FILE_NAME', 'DATE_PUBLISHED', 'DATE_ACCESSED', 'PUBLISHER', 'PUBLISHER_COUNTRY', 'TITLE', 'AUTHOR', 'LINK', 'ARCHIVE_LINK'])
        newRow.at['0', 'FILE_NAME'] = filename
        newRow.at['0', 'DATE_PUBLISHED'] = ''
        newRow.at['0', 'DATE_ACCESSED'] = time.strftime("%m/%d/%Y")
        newRow.at['0', 'PUBLISHER'] = link.publisher
        newRow.at['0', 'PUBLISHER_COUNTRY'] = ''
        newRow.at['0', 'TITLE'] = link.title
        newRow.at['0', 'AUTHOR'] = "Staff"
        newRow.at['0', 'LINK'] = link.links[0]
        newRow.at['0', 'ARCHIVE_LINK'] = link.links[1] if len(link.links) > 1 else ''

        return newRow

    def add_row(self, path, new_row):
        xl = pd.read_excel(path)
        xl = pd.concat([xl, new_row])
        writer = pd.ExcelWriter(path, engine='xlsxwriter')
        xl.to_excel(writer, 'Sheet1', index=False)
        writer.save()

    def make_rdf(self, title, link, direc):
        xml = ("""<?xml version="1.0"?>
<RDF:RDF xmlns:MAF="http://maf.mozdev.org/metadata/rdf#"
         xmlns:NC="http://home.netscape.com/NC-rdf#"
         xmlns:RDF="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <RDF:Description RDF:about="urn:root">
    <MAF:originalurl RDF:resource="{0}"/>
    <MAF:title RDF:resource="{1}"/>
    <MAF:archivetime RDF:resource="{2}"/>
    <MAF:indexfilename RDF:resource="index.html"/>
    <MAF:charset RDF:resource="UTF-8"/>
  </RDF:Description>
</RDF:RDF>""").format(link, title, datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S EST"))
        with open(direc + "/index.rdf", "w") as rdf_file:
            print("{}".format(xml.strip()), file=rdf_file)

    def record_source(self, base_dir, l, dir_name):
        # dir/html/subdir
        if(self.fetch_html(l, base_dir + "/" + dir_name)):
            self.make_rdf(l.title, l.links[0], base_dir + "/" + dir_name)
            self.seen_links[l.links[0].strip()] = '1'
            if len(l.links) > 1:
                self.seen_links[l.links[1].strip()] = '1'
            return self.make_row(dir_name, l)
        else:
            self.seen_links[l.links[0].strip()] = '1'
            if len(l.links) > 1:
                self.seen_links[l.links[1].strip()] = '1'
            return None
        # shutil.make_archive(base_dir + "/" + dir_name, 'zip', base_dir, dir_name)
        # os.rename(base_dir + "/" + dir_name + ".zip", base_dir + "/" + dir_name + ".html.maff")
        # shutil.rmtree(base_dir + "/" + dir_name)

        # archive
        # if (len(l.links) > 1):
        #     if(self.fetchHtml(l.links[0], base_dir + "/" + dir_name + "_archived")):
        #         print()
        #         # self.makeRdf(l.title, l.links[0], base_dir + "/" + dir_name + "_archived")
        #         # shutil.make_archive(base_dir + "/" + dir_name + "_archived", 'zip', base_dir, dir_name + "_archived")
        #         # os.rename(base_dir + "/" + dir_name + "_archived" + ".zip", base_dir + "/" + dir_name + "_archived" + ".html.maff")
        #         # shutil.rmtree(base_dir + "/" + dir_name + "_archived")
        #     else:
        #         print('bad archive link, skipping...')

    #make a dict with each line (ie. link) in text file
    def load_seen_links(self, path):
        with open(path, "r") as text_file:
            for l in text_file:
                if(l != '\n'):
                    self.seen_links[l.strip()] = '1'
            for k, v in self.seen_links.items():
                print("prev " + k)

    def write_link_file(self, path):
        with open(path, 'w') as text_file:
            lines = []
            for k, v in self.seen_links.items():
                print(k.strip(), file = text_file)


#load file with prev. links into memory, hash against it.
#load links into some data structure
#feed each element in that data structure to html getter with the name of the folder it'll be saved in
#at the same time save to an excel file

txt = "/Users/andrescremisini/Documents/Cognac/misc/ukr/ukr_links.txt"
xl = '/Users/andrescremisini/Documents/Cognac/misc/ukr/ukr_list.xlsx'
base_dir = "/Users/andrescremisini/Documents/Cognac/misc/ukr/ukr_news"
event_name = "ukr_"
fnum = 794

sources = ['https://en.wikipedia.org/wiki/Ukrainian_crisis',
        'https://en.wikipedia.org/wiki/Timeline_of_the_Euromaidan',
        'https://en.wikipedia.org/wiki/Ukraine%E2%80%93European_Union_Association_Agreement',
        'https://en.wikipedia.org/wiki/2014_Hrushevskoho_Street_riots',
        'https://en.wikipedia.org/wiki/2014_Euromaidan_regional_state_administration_occupations',
        'https://en.wikipedia.org/wiki/2014_Ukrainian_revolution',
        'https://en.wikipedia.org/wiki/Annexation_of_Crimea_by_the_Russian_Federation',
        'https://en.wikipedia.org/wiki/Timeline_of_the_annexation_of_Crimea_by_the_Russian_Federation',
        'https://en.wikipedia.org/wiki/2014_pro-Russian_unrest_in_Ukraine',
        'https://en.wikipedia.org/wiki/Russian_military_intervention_in_Ukraine_(2014%E2%80%93present)',
        'https://en.wikipedia.org/wiki/War_in_Donbass',
        'https://en.wikipedia.org/wiki/Ukrainian_presidential_election,_2014',
        'https://en.wikipedia.org/wiki/Ukrainian_parliamentary_election,_2014',
        'https://en.wikipedia.org/wiki/Donbass_general_elections,_2014',
        'https://en.wikipedia.org/wiki/Ukrainian_local_elections,_2015',
        'https://en.wikipedia.org/wiki/International_sanctions_during_the_Ukrainian_crisis'
        ]

short_sources = ['https://en.wikipedia.org/wiki/Timeline_of_the_Euromaidan']

wg = WikiRefGetter(txt)
for l in sources:
    html = wg.html_from_link(l)
    clean_links = wg.wiki_soup(html)
    for k, v in clean_links.items():
        new_row = wg.record_source(base_dir, v, event_name + str(fnum))
        wg.add_row(xl, new_row)
        wg.write_link_file(txt)
        fnum = fnum + 1

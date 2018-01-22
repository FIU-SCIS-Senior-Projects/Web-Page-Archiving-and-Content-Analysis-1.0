from bs4 import BeautifulSoup
import urllib.request
import datetime
import os
from openpyxl import load_workbook

def make_rdf(title, link, path):
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
    with open(path + "/index.rdf", "w") as rdf_file:
        print("{}".format(xml.strip()), file=rdf_file)

def wget(url, path):
    cmd = "wget -np -N -k -p -nd -nH -H -E -R mpg,mpeg,mp3,mp4,wav,au,audio.aspx --no-check-certificate -e robots=off -U 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4' -P " + path + " " + "\"" + url.strip() + "\""
    os.system(cmd)
    # make sure wget worked
    if (os.path.exists(path)):
        return True
    else:
        return False

def add_source(url, f_name, event, xl_path, path):
    with urllib.request.urlopen(url) as response:
        html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    title = str(soup.find('title').string).replace(' - Sputnik International', '')
    date = soup.find('meta', {"http-equiv" : 'last-modified'})['content'][:10]
    date = datetime.datetime.strptime(date, "%Y-%m-%d")
    date = date.strftime("%m/%d/%Y")
    #make rdf
    make_rdf(title, url, path=path + '/' + f_name)
    #add to xl
    wb = load_workbook(filename=xl_path)
    ws = wb.active
    ws.append([f_name,
               date,
               datetime.datetime.now().strftime("%m/%d/%Y"),
               'Sputnik',
               'Russia',
               title,
               'Staff',
               event,
               '-1',
               url,
               ''])
    wb.save(xl_path)
    #print(soup.find('meta', {"http-equiv" : 'last-modified'})['content'][:10].replace('-','/'))
    #print(soup.prettify())

    # with open(output_path, "a") as text_file:
    #     print("{}".format(line), file=text_file)

def extract_text(path):
    directory = os.fsencode(path)
    for file in os.listdir(path):
        filename = os.fsdecode(file)
        if filename == 'index.html':
            p = os.path.join(directory.decode("utf-8"), filename)
            with open(p) as html:
                soup = BeautifulSoup(html, 'html.parser')
            header = soup.find('div', {"class": 'b-article__lead'})
            if header is None:
                header = ''
            else:
                header = header.string
            text = soup.find('div', {'itemprop': 'articleBody'})
            for div in text('div'):
                div.decompose()
            with open(path + '/text.txt', 'w') as txt:
                if header == '':
                    print("{}".format(text.get_text().strip()), file=txt)
                else:
                    print("{}".format(header.strip() + '\n' + text.get_text().strip()), file=txt)

sputnik_links = '/Users/andrescremisini/Documents/Cognac/svn/projects/onr/corpora/news/ukraine/sputnik/sputnik_all_running.txt'
data_dir = '/Users/andrescremisini/Documents/Cognac/svn/projects/onr/corpora/news/ukraine/rus'
out = '/Users/andrescremisini/Documents/Cognac/svn/projects/onr/corpora/news/ukraine/ukr_final_adding_rus.xlsx'
f_num = 4495

with open(sputnik_links) as txt_file:
    for line in txt_file:
        url = line.split(' ;; ')[0]
        print('starting ' + str(f_num) + '...')
        if wget(url, path=data_dir + '/ukr_' + str(f_num)):
            add_source(url, f_name='ukr_' + str(f_num), event=line.split(' ;; ')[1].strip(), xl_path=out, path=data_dir)
            extract_text(data_dir + '/ukr_' + str(f_num))
            f_num += 1
        print(str(f_num - 1) + ' done')
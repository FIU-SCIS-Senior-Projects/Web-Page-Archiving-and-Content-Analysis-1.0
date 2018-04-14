from metadata_extractor import MetadataExtractor
import os
import csv
from dicttoxml import dicttoxml
from dateutil.parser import parse
from xml.dom.minidom import parseString
import codecs

"""
Test file that parses all of the reference work from Andres and saves to csv and xml
"""

m = MetadataExtractor()

dir_name="../Reference Work/"
f = open('test.csv','w')
mydict={
    "publishedDate":"",
    "createdDate":"",
    "modifiedDate":"",
    "author":"",
    "header":"",
    "publisher":"",
    "title":"",
    "fileLocation":"",
    "publisherCountry":"",
    "publisherCoordinates":"",
    "language":"",
    "url":""
}
w = csv.DictWriter(f,mydict.keys())
w.writeheader()
a=[]
for folder, subs, files in os.walk(dir_name):
        for filename in files:
            if filename.endswith(".wat"):
                d = m.extract_data_from_wat(os.path.join(folder,filename))
                if not date == {} and d["title"]:
                    if "publishedDate" in d:
                        d["publishedDate"] = parse(d["publishedDate"]).isoformat()
                    if "createdDate" in d:
                        d["createdDate"] = parse(d["createdDate"]).isoformat()
                    if "modifiedDate" in d:
                        d["modifiedDate"] = parse(d["modifiedDate"]).isoformat()
                    d["fileLocation"]=os.path.join(folder,filename)
                    a.append(d)
                    w.writerow(d)
                continue
            elif filename.endswith(".html"):
                d = m.extract_data_from_html(os.path.join(folder,filename))
                if not d == {} and d["title"] and d["title"]!="ns" and d["title"]!="Facebook" and d["title"]!="IFrame" and d["title"]!="Widget Preview" and d["title"]!="Testing Javascript Widget":
                    if "publishedDate" in d:
                        d["publishedDate"] = parse(d["publishedDate"]).isoformat()
                    if "createdDate" in d:
                        d["createdDate"] = parse(d["createdDate"]).isoformat()
                    if "modifiedDate" in d:
                        d["modifiedDate"] = parse(d["modifiedDate"]).isoformat()
                    d["fileLocation"]=os.path.join(folder,filename)
                    a.append(d)
                    w.writerow(d)
                continue
            else:
                continue

f.close()
xml = dicttoxml(a, attr_type=False)
f = codecs.open("test.xml", 'w', encoding='utf-8')
f.write(parseString(xml).toprettyxml())
f.close

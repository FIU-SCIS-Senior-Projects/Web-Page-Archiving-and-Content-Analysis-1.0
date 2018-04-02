from metadata_extractor import MetadataExtractor
import os
import csv
from dicttoxml import dicttoxml
from dateutil.parser import parse
from xml.dom.minidom import parseString
import codecs
# wat_file="/run/media/mfajet/Data/projects/Web-Page-Archiving-and-Content-Analysis-1.0/Code/watapp/outdir/files/15196120301161_theverge.com.wat"
# html_file="/run/media/mfajet/Data/projects/Web-Page-Archiving-and-Content-Analysis-1.0/Code/watapp/outdir/files/15196989105181_tass.com_2/988157.html"

m = MetadataExtractor()
# print m.extract_data_from_wat(wat_file)
# print m.extract_data_from_html(html_file)
#
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
                d = m.extract_data_from_wat(os.path.join(foler,filename))
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


# for filename in os.listdir(dir_name):
#     if filename.endswith(".wat"):
#         d = m.extract_data_from_wat(os.path.join(dir_name,filename))
#         if not ("date" in d and "title" in d and "header" in d and "publisher" in d and "author" in d):
#             print filename
#         w.writerow(d)
#         continue
#     else:
#         continue
f.close()
xml = dicttoxml(a, attr_type=False)
f = codecs.open("test.xml", 'w', encoding='utf-8')
f.write(parseString(xml).toprettyxml())
f.close

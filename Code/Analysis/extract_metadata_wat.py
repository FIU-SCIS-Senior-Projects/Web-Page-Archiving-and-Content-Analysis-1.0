from metadata_extractor import MetadataExtractor
import os
import csv
# wat_file="/run/media/mfajet/Data/projects/Web-Page-Archiving-and-Content-Analysis-1.0/Code/watapp/outdir/files/15196120301161_theverge.com.wat"
# html_file="/run/media/mfajet/Data/projects/Web-Page-Archiving-and-Content-Analysis-1.0/Code/watapp/outdir/files/15196989105181_tass.com_2/988157.html"

m = MetadataExtractor()
# print m.extract_data_from_wat(wat_file)
# print m.extract_data_from_html(html_file)
#
dir_name="../Reference Work/example_output"
f = open('test.csv','w')
mydict={
    "date":"",
    "author":"",
    "header":"",
    "publisher":"",
    "title":""
}
w = csv.DictWriter(f,mydict.keys())
w.writeheader()

for folder, subs, files in os.walk(dir_name):
        for filename in files:
            if filename.endswith(".wat"):
                d = m.extract_data_from_wat(os.path.join(foler,filename))
                if not ("date" in d and "title" in d and "header" in d and "publisher" in d and "author" in d):
                    print filename
                if not date == {}:
                    w.writerow(d)
                continue
            elif filename.endswith(".html"):
                d = m.extract_data_from_html(os.path.join(folder,filename))
                if not ("date" in d and "title" in d and "header" in d and "publisher" in d and "author" in d):
                    print filename
                if not d == {} and not d["title"] == "ns":
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

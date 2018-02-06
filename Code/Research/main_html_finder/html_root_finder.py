import sys
import os
import re

def find_root_html(search_dir):
    html_pattern=re.compile("\"(.*\.html)\"|'(.*\.html)'")

    files = []
    incoming_edges_dict = {}
    for file in os.listdir(search_dir):
        if file.endswith(".html"):
            files.append(file)
            incoming_edges_dict[file]=0
    for file in files:
        for i, line in enumerate(open(os.path.join(search_dir,file))):
            for match in re.finditer(html_pattern, line):
                local_link = match.group(1)
                if local_link in incoming_edges_dict:
                    incoming_edges_dict[local_link] = incoming_edges_dict[local_link] +1
    for k,v in incoming_edges_dict.iteritems():
        if v ==0:
            return k

if __name__ == '__main__':
    find_root_html(sys.argv[1])

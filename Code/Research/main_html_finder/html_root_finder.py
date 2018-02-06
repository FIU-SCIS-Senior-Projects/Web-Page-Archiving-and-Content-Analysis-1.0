import sys
import os
import re

def find_root_html(search_dir):
    html_pattern=re.compile("\"(\\S*\.html)\"|'(\\S\.html)'")

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
                if local_link in incoming_edges_dict and local_link != file:
                    incoming_edges_dict[local_link] = incoming_edges_dict[local_link] +1

    print incoming_edges_dict
    for k,v in incoming_edges_dict.iteritems():
        if v ==0:
            return k

def find_biggest_html(search_dir):
    max_file = None
    for file in os.listdir(search_dir):
        if file.endswith(".html"):
            if not max_file:
                max_file = file
            if (os.path.getsize(os.path.join(search_dir,file))>os.path.getsize(os.path.join(search_dir,max_file))):
                max_file=file
    return max_file

def find_earliest_file(search_dir):
    earliest = None
    for file in os.listdir(search_dir):
        if file.endswith(".html"):
            if not earliest:
                earliest = file
            if (os.path.getmtime(os.path.join(search_dir,file))<os.path.getmtime(os.path.join(search_dir,earliest))):
                earliest=file
    return earliest

def search_wget_output(output):
    lines = output.split("\n")
    for line in lines:
        print line
        pattern = re.compile('.* -> ".*/files/.*/(\S*.html)"')
        for match in re.finditer(pattern, line):
            first_link = match.group(1)
            print first_link
            return first_link

if __name__ == '__main__':
    print find_root_html(sys.argv[1])
    print find_biggest_html(sys.argv[1])
    print find_earliest_file(sys.argv[1])

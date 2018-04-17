import os
import time
import re
import platform
import subprocess
import sys
import shutil
import zipfile
import json
from html_root_finder import *
from dateutil.parser import parse
from bs4 import BeautifulSoup
import geoip2.database
import socket

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
sys.path.append(resource_path('../Analysis'))
from metadata_extractor import MetadataExtractor


def get_domain_name(url):
    """
    Function that takes a url and uses regex to parse out the domain name
    Parameters:
        url: url of website to be downloaded (str)
    Return: Domain name (str)
    """
    exp = '^(?:https?:\/\/)?(?:[^@\/\n]+@)?(?:www\.)?([^:\/\n]+)'
    match = re.search(exp, url)
    if match:
        return match.group(1)

def download_url(url, dest_path, videos=False, suffix=None, rate_limit=None):
    """
    Function to take a url and download it as a single wat file
    Parameters:
        url: url of website to be downloaded (str)
        dest_path: Path to store wat files (str)
        videos: whether to download videos (bool)
        suffix: stting appended to end of filename (str)
        rate_limit: Limit on download speed (str)
    Return: absolute file path of wat file (str)
    """
    site_name = get_domain_name(url)
    timestamp = int(round(time.time() * 10000))
    dest_name = "{0}_{1}".format(timestamp, site_name)
    if suffix:
        dest_name += "_" + str(suffix)

    # Desired flags. Description of what they do can be found in wget manual pages.
    # Do not remove the -nv. This verbosity level states clearly what the index file is.
    flags = "--header 'Accept-encoding: identity' -np -k -p -nd -nH -H -E -nv --no-check-certificate -e robots=off -U 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4'"
    if not videos:
        flags = flags + " -R mpg,mpeg,mp3,mp4,wav,au,audio.aspx,.webm"
    if rate_limit:
        flags = flags + " --limit-rate="+rate_limit
    full_path = os.path.join(dest_path + "/files/", dest_name)

    cmd = "wget " + flags + " -P " + full_path + " " + "\"" + url + "\""

    try:
        # retcode = subprocess.call(cmd, shell=True)
        # if retcode != 0:
        #     print >>sys.stderr, "Child was terminated by signal", retcode
        wget_output = subprocess.check_output(cmd,stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        if e.returncode==8:
            print "An error occurred, but execution continued"
            wget_output = e.output
        else:
            return e.returncode
    except OSError as e:
        print >>sys.stderr, "Execution failed:", e
        return
    link_dest = os.path.join(dest_path, dest_name)

    index_file = search_wget_output(wget_output) #Function comes from html_root_finder

    wat_file = make_wat_file(full_path, os.path.join(dest_path,dest_name),url,index_file)
    return os.path.abspath(wat_file)

def make_wat_file(full_path, dest_path, url, index):
    """
    Function that zips directory with wat structure and renames it as a wat file
    Parameters:
        full_path: path to downloaded files (str)
        dest_path: path to save files (str)
        url: original download url (str)
        index: name of main html file (str)
    Return: wat filename (str)
    """
    #Zip files have errors if the dates are too old on a file which sometimes happens when the metadata is misformatted
    #This loop just mmodifies the file time of any files that are "too old"
    for file in os.listdir(full_path):
        if os.path.getmtime(os.path.join(full_path,file))<=315532800:
            with open(os.path.join(full_path,file), 'a'):
                os.utime(os.path.join(full_path,file), None)

    zf = zipfile.ZipFile(dest_path+".zip", "w", zipfile.ZIP_DEFLATED)
    for dirname, subdirs, files in os.walk(full_path): #Write all downloaded file to /files in zip dir
        for filename in files:
            zf.write(os.path.join(dirname, filename), arcname=os.path.join("files",filename))

    # Write wat information to /wat.json
    wat_info ={
        "url": url,
        "version": "2.0",
        "index": index
    }
    with open(os.path.join(full_path,'wat.json'), 'w') as fp:
        json.dump(wat_info, fp)
    zf.write(os.path.join(full_path,'wat.json'), arcname="wat.json")

    #Extract metadata from html and save it in /extraction/meta.json
    m = MetadataExtractor()
    d = m.extract_data_from_html(os.path.join(full_path,index))

    if "publishedDate" in d:
        try:
            date = parse(d["publishedDate"]).isoformat()
            if ambiguous_date(date):
                d["published_ambiguous"]=True
                d["published_unparsed"]=d["publishedDate"]
            d["publishedDate"] = date
        except:
            d["published_ambiguous"]=True
            d["published_unparsed"]=d["publishedDate"]

    if "createdDate" in d:
        print ""
        try:
            date = parse(d["createdDate"]).isoformat()
            if ambiguous_date(date):
                d["created_ambiguous"]=True
                d["created_unparsed"]=d["createdDate"]
            d["createdDate"] = date
        except:
            d["created_ambiguous"]=True
            d["created_unparsed"]=d["createdDate"]

    if "modifiedDate" in d:
        try:
            date = parse(d["modifiedDate"]).isoformat()
            if ambiguous_date(date):
                d["modified_ambiguous"]=True
                d["modified_unparsed"]=d["modifiedDate"]
            d["modifiedDate"] = date
        except:
            d["modified_ambiguous"]=True
            d["modified_unparsed"]=d["modifiedDate"]

    d["url"]=url
    with open(os.path.join(full_path,'meta.json'), 'w') as fp:
        json.dump(d, fp,indent=4)
    zf.write(os.path.join(full_path,'meta.json'), arcname="extraction/meta.json")

    # Close zip and return wat file name
    zf.close()
    os.rename(dest_path+".zip",dest_path+".wat")
    return dest_path+".wat"

def ambiguous_date(date):
    """
    Parameter:
        date: (str)
    Returns: whether format is ambiguous or not (bool)
    """
    x=re.search(r"^(0?[1-9]|1[0-2])(.|-)(0?[1-9]|1[0-2])(.|-|)[0-9][0-9][0-9]?[0-9]?$",date)
    if x:
        return True
    return False

# Deprecated functions
def make_symlink(source_path, link_name):
    os.symlink(source_path, link_name)

def make_url_file(source_path,file_loc_name):
    source_absolute = os.path.abspath(source_path)
    file_contents = """[InternetShortcut]
URL=file://"""+source_absolute+"""
IconIndex=0"""
    file_loc = open(file_loc_name + ".url", "w")
    file_loc.write(file_contents)
    file_loc.close()

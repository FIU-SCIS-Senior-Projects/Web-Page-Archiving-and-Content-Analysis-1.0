import os
import time
import re
import platform
import subprocess
import sys
import shutil
sys.path.append("../Research/main_html_finder/")
from html_root_finder import *

def get_domain_name(url):
	exp = '^(?:https?:\/\/)?(?:[^@\/\n]+@)?(?:www\.)?([^:\/\n]+)'
	match = re.search(exp, url)
	if match:
		return match.group(1)

def download_url(url, dest_path, videos=False, suffix=None, rate_limit=None):
	site_name = get_domain_name(url)
	timestamp = int(round(time.time() * 10000))
	dest_name = "{0}_{1}".format(timestamp, site_name)
	if suffix:
		dest_name += "_" + str(suffix)

	flags = "-np -N -k -p -nd -nH -H -E -nv --no-check-certificate -e robots=off -U 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4'"
	if not videos:
		flags = flags + " -R mpg,mpeg,mp3,mp4,wav,au,audio.aspx,.webm"
	if rate_limit:
		flags = flags + " --limit-rate="+rate_limit
	full_path = os.path.join(dest_path + "/files/", dest_name)

	cmd = "wget " + flags + " -P " + full_path + " " + "\"" + url + "\""

	try:
	    # retcode = subprocess.call(cmd, shell=True)
	    # if retcode != 0:
		# 	print >>sys.stderr, "Child was terminated by signal", retcode
		wget_output = subprocess.check_output(cmd,stderr=subprocess.STDOUT, shell=True)
	except subprocess.CalledProcessError as e:
		if e.returncode==8:
			print "error but might be okay. We need to figure out when it's okay and when it isn't"
			wget_output = e.output
		else:
			return e.returncode
	except OSError as e:
		print >>sys.stderr, "Execution failed:", e
		return
	link_dest = os.path.join(dest_path, dest_name)

	# index file = find_root_html(full_path)
	index_file = search_wget_output(wget_output)
	f=open(os.path.join(full_path,"wat_link.txt"),"w")
	f.write(index_file)
	f.close()
	source_path = os.path.join("./files/" + dest_name + "/",index_file)

	if platform.system()=="Linux":
		make_symlink(source_path, link_dest)
	else:
		make_url_file(os.path.join(dest_path,source_path),link_dest)
	make_wat_file(full_path)
	return os.path.exists(dest_path)


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

def make_wat_file(full_path):
	for file in os.listdir(full_path):
		if os.path.getmtime(os.path.join(full_path,file))<=315532800:
			with open(os.path.join(full_path,file), 'a'):
				os.utime(os.path.join(full_path,file), None)
	shutil.make_archive(full_path, 'zip', full_path)
	os.rename(full_path+".zip",full_path+".wat")

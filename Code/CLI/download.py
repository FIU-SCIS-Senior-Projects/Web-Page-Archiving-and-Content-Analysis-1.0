import os
import time
import re

def get_domain_name(url):
	exp = '^(?:https?:\/\/)?(?:[^@\/\n]+@)?(?:www\.)?([^:\/\n]+)'
	match = re.search(exp, url)
	if match:
		return match.group(1)

def download_url(url, dest_path, videos=False, suffix=None):
	site_name = get_domain_name(url)
	timestamp = int(round(time.time() * 10000))
	dest_name = "{0}_{1}".format(timestamp, site_name)
	if suffix:
		dest_name += "_" + str(suffix)

	flags = "-np -N -k -p -nd -nH -H -E --no-check-certificate -e robots=off -U 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4'"
	if not videos:
		flags = flags + " -R mpg,mpeg,mp3,mp4,wav,au,audio.aspx"

	full_path = os.path.join(dest_path + "/files/", dest_name)

	cmd = "wget " + flags + " -P " + full_path + " " + "\"" + url + "\""
	os.system(cmd)
	link_dest = os.path.join(dest_path, dest_name)
	for file in os.listdir(full_path):
	    if file.endswith(".html"):
			source_path = os.path.join("./files/" + dest_name + "/",file)
			break
			
	make_symlink(source_path, link_dest)
	return os.path.exists(dest_path)


def make_symlink(source_path, link_name):
	os.symlink(source_path, link_name)
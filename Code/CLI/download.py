import os
import time
import re
import platform

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
	if platform.system()=="Linux":
		make_symlink(source_path, link_dest)
	elif platform.system()=="Darwin":
		make_fileloc(os.path.join(dest_path,source_path),link_dest)
	else:
		print "links not yet supported for this platform"
	return os.path.exists(dest_path)


def make_symlink(source_path, link_name):
	os.symlink(source_path, link_name)
def make_fileloc(source_path,file_loc_name):
	source_absolute = os.path.abspath(source_path)
	file_contents = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>URL</key>
	<string>file://"""+ source_absolute+"""</string>
</dict>
</plist>"""
	file_loc = open(file_loc_name + ".fileloc", "w")
	file_loc.write(file_contents)
	file_loc.close()

import os
import time

def download_url(url, destpath, videos=False, suffix=None):
	site_name = "theverge"
	timestamp = int(round(time.time() * 10000))
	dest_name = "{0}_{1}".format(timestamp, site_name)
	if suffix:
		dest_name += "_" + str(suffix)

	flags = "-np -N -k -p -nd -nH -H -E --no-check-certificate -e robots=off -U 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4'"
	if not videos:
		flags = flags + " -R mpg,mpeg,mp3,mp4,wav,au,audio.aspx"

	full_path = os.path.join(destpath, dest_name)

	cmd = "wget " + flags + " -P " + full_path + " " + "\"" + url + "\""
	os.system(cmd)
	return os.path.exists(destpath)

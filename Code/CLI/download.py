import os
import time

def download_url(url, dest_path, videos=False, suffix=None):
	site_name = "theverge"
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
	for file in os.listdir(full_path):
		    if file.endswith(".html"):
				cmd = "ln -s " + os.path.join("./files/" + dest_name + "/",file) + " " + os.path.join(dest_path,dest_name)
				break
	os.system(cmd)
	return os.path.exists(dest_path)

import argparse
import os
import concurrent.futures
import sys
import shutil
from download import download_url

def download_output_wrapper(URL_num, URL, destpath, videos, i, rate_limit):
	print "Downloading URL #" + URL_num + ": " + URL +"\n"
	sys.stdout.flush()
	data = download_url( URL, destpath, videos, i, rate_limit)
	print "Finished for URL #" + URL_num + ": " + URL +"\n"
	sys.stdout.flush()
	return data

def main():
	#add command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("-f", "--file", help="File containing list of URLs", type=file,  required=True)
	parser.add_argument("-d", "--outdir", help="Output directory", type=str)
	parser.add_argument("--rate_limit", help="Value to limit requests. Ex 50k for 50kb/s",dest='rate_limit', type=str)
	parser.add_argument("--videos", help="Include videos and audio",dest='videos', action='store_true')
	parser.add_argument("-m", "--threads", help="Download sites using multiple threads", type=int)
	parser.set_defaults(outdir="./outdir")
	parser.set_defaults(rate_limit="")
	parser.set_defaults(videos=False)
	parser.set_defaults(threads=1)

	args = parser.parse_args()

	# Parse file and args
	destpath = args.outdir
	videos = args.videos
	line = args.file.readline()
	URLS=[]
	while line:
		url = line.strip()
		URLS.append(url)
		line = args.file.readline()
	print str(len(URLS)) + " URLS found" +"\n"
	sys.stdout.flush()

	# run downloads in thread pool executor
	num_threads=args.threads
	with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
		future_to_url = {executor.submit(download_output_wrapper,str(i),URLS[i], destpath, videos, i, args.rate_limit): i for i in range(0,len(URLS))}
		for future in concurrent.futures.as_completed(future_to_url):
			i = future_to_url[future]
			try:
				data = future.result()
				print "URL #" + str(i) + ": " + URLS[i] + " can be found at " + str(data) +"\n"
				sys.stdout.flush()
			except Exception as exc:
				print('%r generated an exception: %s' % (url, exc))
	shutil.rmtree(os.path.join(destpath,"files"))


if __name__ == "__main__":
	main()

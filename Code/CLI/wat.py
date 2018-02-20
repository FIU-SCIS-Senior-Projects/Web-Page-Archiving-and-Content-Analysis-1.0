import argparse
import os
import concurrent.futures
from download import download_url

def main():
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


	destpath = args.outdir
	videos = args.videos
	line = args.file.readline()
	URLS=[]
	while line:
		url = line.strip()
		URLS.append(url)
		line = args.file.readline()
	num_threads=args.threads
	with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
		future_to_url = {executor.submit(download_url,URLS[i], destpath, videos, i, args.rate_limit): URLS[i] for i in range(0,len(URLS))}
		for future in concurrent.futures.as_completed(future_to_url):
			url = future_to_url[future]
			try:
				data = future.result()
				print data
			except Exception as exc:
				print('%r generated an exception: %s' % (url, exc))

if __name__ == "__main__":
	main()

import argparse
import os

from download import download_url

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-f", "--file", help="File containing list of URLs", type=file,  required=True)
	parser.add_argument("-d", "--outdir", help="Output directory", type=str)
	parser.add_argument("--rate_limit", help="Value to limit requests. Ex 50k for 50kb/s",dest='rate_limit', type=str)
	parser.add_argument("--videos", help="Include videos and audio",dest='videos', action='store_true')
	parser.set_defaults(outdir="./outdir")
	parser.set_defaults(rate_limit="")
	parser.set_defaults(videos=False)

	args = parser.parse_args()

	line = args.file.readline()
	count = 1
	while line:
		url = line.strip()
		destpath = args.outdir
		videos = args.videos
		download_url(url, destpath, videos, count, args.rate_limit)
		line = args.file.readline()
		count += 1


if __name__ == "__main__":
	main()

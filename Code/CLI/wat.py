import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", help="File containing list of URLs", type=file,  required=True)
parser.add_argument("-d", "--outdir", help="Output directory", type=str)
parser.add_argument("--rate_limit", help="Boolean value to limit requests",dest='rate_limit', action='store_true')
parser.add_argument("--videos", help="Include videos and audio",dest='videos', action='store_true')
parser.set_defaults(outdir="./")
parser.set_defaults(rate_limit=False)
parser.set_defaults(videos=False)
args = parser.parse_args()
flags = "-np -N -k -p -nd -nH -H -E --no-check-certificate -e robots=off -U 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4'"
if not args.videos:
    flags = flags + "-R mpg,mpeg,mp3,mp4,wav,au,audio.aspx"

line = args.file.readline()
cnt = 1
while line:
    cmd = "wget " + flags + " -P " + args.outdir + " " + "\"" + line.strip() + "\""
    print cmd
    line = args.file.readline()

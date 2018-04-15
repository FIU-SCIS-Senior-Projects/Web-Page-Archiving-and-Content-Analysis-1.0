- python_files/sputnik.py generated everything in /example_output. the code currently dumps text files in the archive folder, but this should happen in a separate folder with corresponding file names, as you’ll see in /example_output.
- python_files/WikiRefGetter.py generated everything in to_parse. The first step of this project will probably be extracting all of the text from the files named index.html. Note that this code does not name the files index.html, as this was done manually. Your downloader code should do this automatically.

City database needs to be downloded from [here](https://dev.maxmind.com/geoip/geoip2/geolite2/) and placed in "Code/Analysis/geo_db"

wget must be installed
npm must be installed
node must be installed (latest version. If you have too early a version you won't be able to build)

python dependencies:
dicttoxml
dateutil.parser
xml.dom.minidom
geoip2.database
concurrent.futures
urllib

Must run ```npm install``` in the watapp directory
Must run ```pip install -r requirements.txt```

run ```npm run dist``` in the watapp directory to build the program
run the created program in whatever way is appropriate for your system.

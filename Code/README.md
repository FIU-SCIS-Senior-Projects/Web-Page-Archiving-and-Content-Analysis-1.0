## Software Dependencies
City database needs to be downloded from [here](https://dev.maxmind.com/geoip/geoip2/geolite2/) and placed in "Code/Analysis/geo_db"  

wget must be installed  
npm must be installed  
node must be installed (latest version. If you have too early a version you won't be able to build)  

#### python dependencies:
* dicttoxml
* dateutil.parser
* xml.dom.minidom
* geoip2.database
* concurrent.futures
* urllib

#### JS Dependencies
* "decompress-zip": "^0.3.0",
* "electron-store": "^1.3.0",
* "fs-extra": "^5.0.0",
* "electron": "~1.7.8",
* "electron-builder": "^19.56.0"



## Installation:
```
git clone https://github.com/FIU-SCIS-Senior-Projects/Web-Page-Archiving-and-Content-Analysis-1.0.git
cd Web-Page-Archiving-and-Content-Analysis-1.0/Code
pip install -r requirements.txt
cd watapp
npm install
npm run dist
```
The program should now be bundled and created
You can find it in the dist folder and you can run it how you run any other program.

## Reference Work
- python_files/sputnik.py generated everything in /example_output. the code currently dumps text files in the archive folder, but this should happen in a separate folder with corresponding file names, as you’ll see in /example_output.
- python_files/WikiRefGetter.py generated everything in to_parse. The first step of this project will probably be extracting all of the text from the files named index.html. Note that this code does not name the files index.html, as this was done manually. Your downloader code should do this automatically.

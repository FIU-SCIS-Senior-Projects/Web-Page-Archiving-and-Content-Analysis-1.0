chmod +x wat_open
cp wat_open /usr/bin/
cp wat.desktop /usr/share/applications/wat.desktop
#Create new mime type using wat-mime.xml
mkdir /usr/share/mime/packages
cp wat-mime.xml /usr/share/mime/packages/wat-mime.xml
update-mime-database /usr/share/mime

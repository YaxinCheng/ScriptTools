#/bin/sh

name="*$1*.zip"
count=$(ls name | wc -l)
echo $count
unzip ${name} 
rm -rf __MACOSX
echo "Unzipped"

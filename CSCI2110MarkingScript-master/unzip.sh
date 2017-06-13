#/bin/sh

name="*$1*.zip"
count=$(ls $name | wc -l)
if [[ $count -eq 1 ]] ; then
	unzip ${name} -d assign
	rm -rf assign/__MACOSX
	echo "Unzipped"
fi

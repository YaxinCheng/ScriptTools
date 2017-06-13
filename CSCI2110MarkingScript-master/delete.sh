#!/bin/sh

rm -rf assign
if [[ "$1" != "" ]] ; then
	rm *$1*
else
	echo "Can't find $1"
fi

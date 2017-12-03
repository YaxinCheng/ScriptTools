#!/bin/sh

if [ $# -eq 2 ]; then
	dir="/Users/cheng/$2"
	if [ "$1" = "-u" ]; then
		umount "$dir"
		rmdir "$dir"
		rm "/Users/cheng/Desktop/$2"
	else
		mkdir "$dir"
		sshfs $1 $dir -o volname=$2
		ln -s "$dir" "/Users/cheng/Desktop/$2"
	fi
elif [ $# -eq 1 ]; then
	if [ "$1" = "-b" ]; then
		echo "Connecting to bluenose"
		dir="/Users/cheng/Bluenose"
		mkdir $dir
		sshfs "ycheng@bluenose.cs.dal.ca:/users/cs/ycheng" $dir -o volname="Bluenose"
		ln -s "$dir" "/Users/cheng/Desktop/Bluenose"
	elif [ "$1" = "-m" ]; then
		echo "Connecting to zhuming4"
		dir="/Users/cheng/zhuming4"
		mkdir $dir
		sshfs "zhuming4@teach.cs.utoronto.ca:/h/u6/c5/02/zhuming4/" $dir -o volname="zhuming4"
		ln -s "$dir" "/Users/cheng/Desktop/zhuming4"
	elif [ "$1" = "-h" ]; then
		echo "Connect to a host:    smount HOST DISK"
		echo "Disconnect to a host: smount -u DISK"
	else
		echo "Unsupported shortchut"
	fi
else
	echo "Connect to a host:    smount HOST DISK"
	echo "Disconnect to a host: smount -u DISK"
fi

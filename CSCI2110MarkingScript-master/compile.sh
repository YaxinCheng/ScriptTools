#!/bin/sh

count=$(ls *class | wc -l)
if [[ "$1" == "-f" ]] ; then
	javac *.java
elif [[ $count -eq 0 ]] ; then
	comment1=$(grep -R '//' .| wc -l)
	comment2=$(grep -R '/\*' . | wc -l)
	echo "comments count: $((comment1 + comment2))"
	javac *.java
fi
grep -Ri 'public static void main' .
#java PracticeMoves

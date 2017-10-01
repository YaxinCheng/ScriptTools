#!/bin/sh

count=$(ls *class | wc -l)
if [[ $count -eq 0 ]] ; then
	abstractCount=$(grep -R abstract .| wc -l)
	flexibleCount=$(ls FlexiblePiece.java | wc -l)
	echo "abstract exist: $abstractCount"
	echo "Flexible exist: $flexibleCount"
	javac *.java
fi

java PracticeMoves

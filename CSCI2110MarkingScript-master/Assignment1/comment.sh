#!/bin/sh

c1=$(grep -R "//" . | wc -l)
c2=$(grep -R "/\*" . | wc -l)
echo $(($c1+$c2))

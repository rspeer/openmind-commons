#!/bin/bash
input="$1"
output="${input/.dot/}.gv.txt"
dot "$input" -Txdot -o"$output"

#!/bin/bash
# The is a sample script to run the layer 0 for different position of UE.
# One can add x,y,z parameters as input to the python test.py file. Laye 0 will create folders based on the UE position and generate JSON files inside that directory
process () {
  python3 test.py $1 $2 0
  dir_name=ue_x$1_y$2
  mkdir $dir_name
  mv bs_* $dir_name
}

x=25
y=27

while [ $y -le 27 ]
do
  process $x $y
  (( y+=2 ))
done

echo Process Complete 

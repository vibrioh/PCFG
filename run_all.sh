#!/usr/bin/env bash

echo "run q4"

python parser.py q4 parse_train.dat parse_train.RARE.dat


echo "run q5"

echo "start at"
date +%s

python parser.py q5 parse_train.RARE.dat parse_dev.dat q5_prediction_file

echo "end at"
date +%s

python eval_parser.py parse_dev.key q5_prediction_file > q5_eval.txt


echo "run q6"

python parser.py q4 parse_train_vert.dat parse_train_vert.RARE.dat

echo "start at"
date +%s

python parser.py q6 parse_train_vert.RARE.dat parse_dev.dat q6_prediction_file

echo "end at"
date +%s

python eval_parser.py parse_dev.key q6_prediction_file > q6_eval.txt
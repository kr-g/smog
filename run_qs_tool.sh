#!/bin/bash


black . --exclude .venv
flake8 --config flake8.cfg --exclude .venv
python3 -m unittest -v


for f in build dist *.egg-info __pycache__ ; do 
    echo remove $f
    find . -name $f | xargs rm -rf
done


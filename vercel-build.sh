#!/bin/bash
# Install Python 3.9
curl -O https://www.python.org/ftp/python/3.9.18/Python-3.9.18.tgz
tar xzf Python-3.9.18.tgz
cd Python-3.9.18
./configure --enable-optimizations
make -j $(nproc)
make install
cd ..

# Install pip for Python 3.9
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3.9 get-pip.py

# Install dependencies
python3.9 -m pip install -r requirements.txt 
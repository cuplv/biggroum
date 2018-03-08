#!/bin/bash
# Initial script to run the extraction on openstack


# install java
sudo apt-get install openjdk-7-jdk
# build tools to compile protobuf
sudo apt-get -y install build-essential
# sbt
echo "deb https://dl.bintray.com/sbt/debian /" | sudo tee -a /etc/apt/sources.list.d/sbt.list
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2EE0EA64E40A89B84B2DF73499E82A75642AC823
sudo apt-get update
sudo apt-get -y install sbt
# protobuf
wget https://github.com/google/protobuf/releases/download/v2.6.1/protobuf-2.6.1.tar.gz
tar -xzvf protobuf-2.6.1.tar.gz
pushd protobuf-2.6.1 && ./configure --prefix=/usr && make && sudo make install && popd


#pygit2

sudo apt-get install libssh2-1 libssh2-1-dev

# libgit2 - updated version
sudo apt-get install cmake
pushd .
mkdir /tmp/_appdir
cd /tmp/_appdir
wget https://github.com/libgit2/libgit2/archive/v0.24.1.tar.gz
tar xzf v0.24.1.tar.gz
cd libgit2-0.24.1/
cmake .
make -j
sudo make install
sudo ldconfig

sudo apt-get install pip
sudo apt-get install python-dev
sudo apt-get install python-six
sudo apt-get install python-cffi
sudo pip install pygit2


# ANDROID STUDIO

# to run aapt
sudo apt-get install lib32stdc++6 lib32z1


# 1. Feature extractor
git clone --depth=50 --branch=master git@github.com:cuplv/FixrGraphExtractor.git cuplv/FixrGraphExtractor
pushd cuplv/FixrGraphExtractor && sbt oneJar && popd


# 2. Get extractor script
git clone --depth=50 --branch=master git@git.cs.colorado.edu:fixr/api-program-graphs.git


# Print configuration
java -Xmx32m -version
javac -J-Xmx32m -version


# Run the extraction



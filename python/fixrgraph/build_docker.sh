#!/bin/bash
cp ../../FixrGraphExtractor/target/scala-2.12/fixrgraphextractor_2.12-0.1.0-one-jar.jar .
docker build -t fixrgraph_muse:latest .


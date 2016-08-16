# Example of run of the extraction
`python run_extractor.py -a ./test.json -i /tmp/in_repo -g /tmp/graph_dir -p /tmp/prov_dir -f android -j /home/sergio/works/projects/muse/repos/FixrGraphExtractor/target/scala-2.10/fixrgraphextractor_2.10-0.1-SNAPSHOT-one-jar.jar -l /home/sergio/works/projects/muse/repos/FixrGraphExtractor/src/test/resources/libs/android-17.jar`

You need a working android sdk in order to perform the extraction.

I will update the README with more information on dependencies.



# Current issue with the automatic extraction
- Soot requires all the set of dependencies of the application to succesfully parse the bytecode and generate the ACDFGs.
- The set of dependencies is specified in gradle, but we don't have it explicitly in an easy way.
- The other issue is getting the location of the jar files of the dependencies

  


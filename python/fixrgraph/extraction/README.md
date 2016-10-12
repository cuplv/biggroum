# Automatic script used to run the extraction

# Description
The script `run_extractor.py` download a list of repos from github (at a specific commit version), tries to compile the android apps in the repos and run the extractor on them.


# Dependencies

- Android SDK: you need a working android sdk in order to perform the extraction (setting the ANDROIDHOME environment variable)

- You need to have build the oneJar for the extractor. In the <path_to_the_extractor> folder run `sbt oneJar`

- Python and pygit2



# Run the extractor
Example on how to use the extractor on the smaller set of repos:

Create a directory to store the results: `$> mkdir <path_to_results>`

Run the extraction: ```python run_extractor.py  -a ./examples/smaller.json  -i <paths_to_results>/src_repo -g <paths_to_results>/graphs -p <paths_to_results>/provenance -f android -j <path_to_the_extractor>/target/scala-2.11/fixrgraphextractor_2.11-0.1-SNAPSHOT-one-jar.jar```




# Current issue with the automatic extraction
- Soot requires all the set of dependencies of the application to succesfully parse the bytecode and generate the ACDFGs.
- The set of dependencies is specified in gradle, but we don't have it explicitly in an easy way.
- The other issue is getting the location of the jar files of the dependencies

  


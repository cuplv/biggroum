# Solr configuration for the GROUMs documents

# Create Solr core
```
solr start -d server/ -s server/solr
solr create -c groums
solr stop
```

# Configuring our core
Steps took from Ken's guide https://github.com/kenbod/sysadmin/blob/master/solr.md

The default configuration represents a great start. I'm going to change it to serve my own needs. YMMV.

First: head to the core's configuration directory. On my machine that directory is:

`/srv/hdfs-0/data/server/solr/fixr/conf`

Second: There is a file in this directory called `managed-schema`. Rename it `schema.xml`.

Third: Make the following edits.

1. Find the two lines that look like this:

  `<field name="_text_" type="text_general" indexed="true" stored="false" multiValued="true"/>`

  `<copyField source="*" dest="_text_"/>`
  
  Delete them.
  
2. Find the line that looks like this:

  `<dynamicField name="*_s"  type="string"  indexed="true"  stored="true" />`
  
  Add the following line, right under it:
  
  `<dynamicField name="*_sni"  type="string"  indexed="false"  stored="true" />`
  
  This allows us to store text fields in our documents that are not analyzed or indexed but are stored so that they can later be retrieved. We only want these fields so we can display them as the result of a query but we are not going to be searching on their content.


# Configure Solr to run as its own user
See Ken's guide https://github.com/kenbod/sysadmin/blob/master/solr.md

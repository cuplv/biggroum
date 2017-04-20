# Import the graphs, clusters and patterns data into Solr

1. Import graphs

```
python import_clusters.py -g /tmp/testextraction/graphs -p /tmp/testextraction/provenance -s 'http://localhost:8983/solr/groums'
```


2. Import clusters and patterns

```
python import_clusters.py  -c /tmp/testextraction/clusters/ -s 'http://localhost:8983/solr/groums'
```

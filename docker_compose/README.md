The docker compose runs the docker containers for the biggroum search.

The `docker-compose.yml` is generated from the file `get_docker_compose.py`.

# Deploy

## Local
``` python get_docker_compose.py
```
Will generate a the docker compose file from the local image registry.

Once the `docker-compose.yml` file is generated, the container can be spun up
with:

```docker-compose up -d
```

## Two six lab infrastructure

``` python get_docker_compose.py -r -v 0.2
```

will generate a the docker compose file from the nexus image registry (the one
used in the two-six lab deployment) tagging the images with version 0.2.

*NOTE*: You can run the script `tag_and_commit.bash` to directly:
- Tag the images with a version (change the current version in the file)
- Push the new images  on the nexus docker registry
- Generate the `docker-compose.yml` file


# Test

## Local

Run the tests to see if everything is ok:

```python test.py  --address localhost --search_port 30072  --solr_port 30071 --webserver_port 30073
```

If you get an error, you can get more info enabling the debug output:

```python test.py  --address localhost --search_port 30072  --solr_port 30071 --webserver_port 30073 -d
```


The web interface should be accessible at the address `http://localhost:30073`

To test the web interface now, insert the following input and press `Search`:

- User/Repo: `denzilferreira/aware-client`
- CommitId: `537e709dedefba23255700be8af028ea415f3923`
- Method name: `com.aware.Bluetooth_notifyMissingBluetooth`
- File name: `Bluetooth.java`
- Line number: `331`


## Two six lab infrastructure

The services should be up. Run the tests to see if everything is ok:

```python test.py --address 100.120.0.6 --search_port 30072  --solr_port 30071 --webserver_port 30073
```

The web interface should be accessible at the address `http://100.120.0.6:30073`

Use the same input as for the local test.


The docker compose runs the docker containers for the biggroum search.

The `docker-compose.yml` is generated from the file `get_docker_compose.py`.

Running:
``` python get_docker_compose.py
```
Will generate a the docker compose file from the local image registry.

Running:
``` python get_docker_compose.py -r
```
will generate a the docker compose file from the nexus image registry (the one
used in the two-six lab deployment.

Once the `docker-compose.yml` file is generated, the container can be spun up
with:
```docker-compose up -d```

The services should be up. Run the tests to see if everything is ok:
```cd ../docker_solr && python test.py -a localhost -p 30071```

```cd ../docker_search && python test.py -a localhost -p 30072```

The web interface should be accessible at the address `http://localhost:30073`

snn
===

Rainer Dunkels Work


## Docker

to build the docker container, run
```
docker build -t nestsim/nest:3.0 .
```

To start the container, type
```
docker run -it --rm -e LOCAL_USER_ID=`id -u $USER` --name nest -p 5000:5000
            -v $(pwd):/opt/data nestsim/nest:3.0 /bin/bash
```

for more info, see https://github.com/nest/nest-docker


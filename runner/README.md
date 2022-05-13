## Usage for _module_

### Build for _module_
```
$ export DIR=module
$ JFROG_BOT_USERNAME=$JFROG_BOT_USERNAME JFROG_BOT_PASS=$JFROG_BOT_PASS DIR=$DIR docker-compose build
```

### Environment variables
You can change behaviour with the following env variables variables:
- Lib env variables are always needed 

### Run
```
docker-compose up -d
docker exec -it <CONTAINER_ID> bash 
python runner.py -r {YOUR_JSON_RUN_SPEC}
```

In case you dont want to write the run spec in the term itself just try from file as follows.

```
python runner.py -r "$(cat run.json)"
```
You can follow the .template to setup your run

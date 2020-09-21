# async-server-api
asynchronous or multi-core server api

## Getting Started

### apache

```
$ cd apache
$ ./install.sh
$ ./start.sh
$ python stress_test.py
$ ./stop.sh
```

### flask (example)

- requirements
```
$ ./start.sh
$ redis-server    // start redis server
$ redis-cli ping  // test redis server
$ pip install flask gevent requests redis pillow numpy
```

- Start server
```
$ python server.py
```

- Client test
```
$ curl -X POST -F image=@<image> 'http://localhost:5000/predict'
or POSTMAN
$ python test.py
```
## Getting Started

### requirements
```
$ ./start.sh
$ redis-server    // start redis server
$ redis-cli ping  // test redis server
$ pip install flask gevent requests redis pillow numpy
```

### Start server
```
$ python server.py
```

### Client test
```
$ curl -X POST -F image=@<image> 'http://localhost:5000/predict'
or POSTMAN
$ python test.py
```
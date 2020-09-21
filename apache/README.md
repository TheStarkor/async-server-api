
### requirements
```
$ ./start.sh
$ redis-server    // start redis server
$ redis-cli ping  // test redis server
$ pip install flask gevent requests redis pillow numpy
```

### Start server
```
$ python run_model_server.py
$ python run_web_server.py
```

### Client test
```
$ python stress_test.py
```
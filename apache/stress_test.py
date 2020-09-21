from threading import Thread
import requests
import time

KERAS_REST_API_URL = "http://localhost:5000/predict"
IMAGE_PATH = "test.jpg"

NUM_REQUESTS = 500
SLEEP_COUNT = 0.05

def call_prediction_endpoint(n):
    image = open(IMAGE_PATH, "rb").read()
    payload = {"image": image}

    r = requests.post(KERAS_REST_API_URL, files=payload).json()

    if r["success"]:
        print(f"[INFO] thread {n} OK")
        print(time.time() - start)

    else:
        print(f"[INFO] thread {n} FAILED")

start = time.time()
for i in range(NUM_REQUESTS):
    t = Thread(target=call_prediction_endpoint, args=(i,))
    t.daemon = True
    t.start()
    time.sleep(SLEEP_COUNT)

time.sleep(300)
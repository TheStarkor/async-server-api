from tensorflow.keras.applications import ResNet50
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.applications.resnet50 import decode_predictions
from threading import Thread
from PIL import Image
import numpy as np
import base64
import flask
import redis
import uuid
import time
import json
import sys
import io

import tensorflow as tf
 
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
  try:
    # Currently, memory growth needs to be the same across GPUs
    for gpu in gpus:
      tf.config.experimental.set_memory_growth(gpu, True)
    logical_gpus = tf.config.experimental.list_logical_devices('GPU')
    print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
  except RuntimeError as e:
    # Memory growth must be set before GPUs have been initialized
    print(e)

# initialize constants used to control image spatial dimensions and
# data type
IMAGE_WIDTH = 224
IMAGE_HEIGHT = 224
IMAGE_CHANS = 3
IMAGE_DTYPE = "float32"

# initialize constants used for server queuing
IMAGE_QUEUE = "image_queue"
BATCH_SIZE = 32
SERVER_SLEEP = 0.25
CLIENT_SLEEP = 0.25

app = flask.Flask(__name__)
db = redis.StrictRedis(host="localhost", port=6379, db=0)
model = None

def base64_encode_image(img):
    return base64.b64encode(img).decode('utf-8')

def base64_decode_image(img, dtype, shape):
    img = bytes(img, encoding='utf-8')

    img = np.frombuffer(base64.decodestring(img), dtype=dtype)
    img = img.reshape(shape)

    return img

def prepare_image(image, target):
    if image.mode != "RGB":
        image = image.convert("RGB")

    image = image.resize(target)
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    image = preprocess_input(image)

    return image

def classify_process():
    print("* Loading model...")
    model = ResNet50(weights="imagenet")
    print("* Model loaded")

    while True:
        queue = db.lrange(IMAGE_QUEUE, 0, BATCH_SIZE - 1)
        imageIDs = []
        batch = None

        for q in queue:
            q = json.loads(q.decode("utf-8"))
            image = base64_decode_image(q["image"], IMAGE_DTYPE, (1, IMAGE_HEIGHT, IMAGE_WIDTH, IMAGE_CHANS))

            if batch is None:
                batch = image

            else:
                batch = np.vstack([batch, image])

            imageIDs.append(q["id"])

        if len(imageIDs) > 0:
            print(f"* Batch size: {batch.shape}")
            preds = model.predict(batch)
            results = decode_predictions(preds)

            for (imageID, resultSet) in zip(imageIDs, results):
                output = []

                for (imagenetID, label, prob) in resultSet:
                    r = {"label": label, "probability": float(prob)}
                    output.append(r)

                db.set(imageID, json.dumps(output))

            db.ltrim(IMAGE_QUEUE, len(imageIDs), -1)

        time.sleep(SERVER_SLEEP)

@app.route("/predict", methods=["POST"])
def predict():
    data = {"success": False}

    if flask.request.method == "POST":
        if flask.request.files.get("image"):
            image = flask.request.files["image"].read()
            image = Image.open(io.BytesIO(image))
            image = prepare_image(image, (IMAGE_WIDTH, IMAGE_HEIGHT))

            image = image.copy(order="C")

            k = str(uuid.uuid4())
            d = {"id": k, "image": base64_encode_image(image)}
            db.rpush(IMAGE_QUEUE, json.dumps(d))

            while True:
                output = db.get(k)

                if output is not None:
                    output = output.decode("utf-8")
                    data["predictions"] = json.loads(output)

                    db.delete(k)
                    break

                time.sleep(CLIENT_SLEEP)

            data["success"] = True

    return flask.jsonify(data)

if __name__ == "__main__":
    print("* Starting model service...")
    t = Thread(target=classify_process, args=())
    t.daemon = True
    t.start()

    print("* Starting web service...")
    app.run()
import os
from PIL import Image
import time
import numpy as np
import cv2
from pymongo import MongoClient
import io
import base64
import threading
from time import sleep

from utils import delete_folder

client = MongoClient("mongodb://localhost:27017")
db = client["imageLab"]
colorization_collection = db['photos']

def delete_image_collection(user_id):
    sleep(140) # wait for 2 minutes
    colorization_collection.delete_many({'user_id': user_id})

def imgcolorize(image_d,user_id):
    # Paths to load the model
    DIR = r"D:\imagelab"
    PROTOTXT = os.path.join(DIR, r"model/colorization_deploy_v2.prototxt")
    POINTS = os.path.join(DIR, r"model/pts_in_hull.npy")
    MODEL = os.path.join(DIR, r"model/colorization_release_v2.caffemodel")

    # Load the Model
    print("Load model")
    net = cv2.dnn.readNetFromCaffe(PROTOTXT, MODEL)
    pts = np.load(POINTS)

    # Load centers for ab channel quantization used for rebalancing.
    class8 = net.getLayerId("class8_ab")
    conv8 = net.getLayerId("conv8_313_rh")
    pts = pts.transpose().reshape(2, 313, 1, 1)
    net.getLayer(class8).blobs = [pts.astype("float32")]
    net.getLayer(conv8).blobs = [np.full([1, 313], 2.606, dtype="float32")]
    print('Processing')

    # Load the input image
    # image = cv2.imread(image_d)
    image = cv2.imdecode(np.frombuffer(image_d, np.uint8), cv2.IMREAD_COLOR)
    scaled = image.astype("float32") / 255.0
    lab = cv2.cvtColor(scaled, cv2.COLOR_BGR2LAB)
    resized = cv2.resize(lab, (224, 224))
    L = cv2.split(resized)[0]
    L -= 50

    print("Colorizing the image")
    net.setInput(cv2.dnn.blobFromImage(L))
    ab = net.forward()[0, :, :, :].transpose((1, 2, 0))
    ab = cv2.resize(ab, (image.shape[1], image.shape[0]))
    L = cv2.split(lab)[0]
    colorized = np.concatenate((L[:, :, np.newaxis], ab), axis=2)
    colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2BGR)
    colorized = np.clip(colorized, 0, 1)
    colorized = (255 * colorized).astype("uint8")
    # Encode image to base64
    colorized_image_data = cv2.imencode('.JPEG', colorized)[1]
    colorized_image_data = base64.b64encode(colorized_image_data).decode()
    # Encode the binary image to base64
    colorization_collection.insert_one({'user_id': user_id, 'image_data': colorized_image_data, 'type': 'Colored'})
    threading.Thread(target=delete_image_collection, args=(user_id,)).start()
    image_data = base64.b64decode(colorization_collection.find_one({'user_id': user_id,'type': 'Colored'})['image_data'])
    image = Image.open(io.BytesIO(image_data))
    img_io = io.BytesIO()
    image.save(img_io, format= 'JPEG',quality=100)
    img_io.seek(0)
    img_str = base64.b64encode(img_io.getvalue()).decode()
    return img_str
 
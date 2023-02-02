from flask import request, render_template
from PIL import Image
from rembg import remove
import base64
import os
from utils import generate_unique_id
from pymongo import MongoClient
import io
import threading

from time import sleep


# Connect to MongoDB
# client = MongoClient("mongodb+srv://prabin:bprabin@cluster0.2phmxej.mongodb.net/test")
client = MongoClient("mongodb://localhost:27017")
db = client["imageLab"]
bgremoved_collection = db['bgremoved']


def delete_image(user_id):
    sleep(140) # wait for 2 minutes
    bgremoved_collection.delete_one({'user_id': user_id})

def remove_bg():
    file = request.files.get('bfile')
    try:
        if file is None or file.filename == '':
            return 'No file was submitted or the file is empty'
        image = Image.open(file)
        image = remove(image)
        user_id = generate_unique_id()
        img_io = io.BytesIO()
        image.save(img_io, format='PNG')
        img_io.seek(0)
        image_data = img_io.read()
        bgremoved_collection.insert_one({'user_id': user_id, 'image_data': image_data})
        threading.Thread(target=delete_image, args=(user_id,)).start()
        image_data = bgremoved_collection.find_one({'user_id': user_id})['image_data']
        image = Image.open(io.BytesIO(image_data))
        img_io = io.BytesIO()
        image.save(img_io, format='PNG')
        img_io.seek(0)
        img_str = base64.b64encode(img_io.getvalue()).decode()
        return render_template('result.html',message="Background Removed Successfully",user_id=user_id ,image_data=img_str,format=format)
    except OSError:
        return render_template("error.html",error_msg='Upload a valid image file.')

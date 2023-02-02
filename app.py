import os
from flask import Flask, request, render_template,Response,make_response
from imgColorization import imgcolorize
from PIL import Image
from conversions import convert_to_jpg, convert_to_png, convertgif_toimg, convertto_art, convertto_grayscale, compress_image, convertto_gif
from removebg import remove_bg
from utils import generate_unique_id, delete_folder
import threading
from pdftools import compress_pdf,convert_pdf
import io
import time
import numpy as np
import cv2
import base64


from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
# client = MongoClient("mongodb+srv://prabin:bprabin@cluster0.2phmxej.mongodb.net/test")

db = client["imageLab"]
pdf_collection = db["pdf_files"]
bgremoved_collection = db['bgremoved']
image_collection = db['Images']
colorization_collection = db['photos']

app = Flask(__name__, template_folder='templates', static_folder='static',)


@app.route("/")
def hello_world():
    return render_template("index.html")

@app.route("/pdftool")
def pdftools():
    return render_template("pdftool.html")

@app.route("/colorize")
def colorize():
    return render_template("colorize.html")

@app.route("/about")
def about():
    return render_template("about.html")


@app.route('/pngtojpgconvert', methods=['POST'])
def png_to_jpg():
    return convert_to_jpg()

@app.route('/bgremove', methods=['POST']) 
def background_remove():
    return remove_bg()

@app.route('/jpgtopngconvert', methods=['POST'])
def jpg_to_png():
    return convert_to_png()

@app.route('/topencilart', methods=['POST'])
def image_to_pencilart():
   return convertto_art()

@app.route('/tograyscale', methods=['POST'])
def to_grayscale():
   return convertto_grayscale()

@app.route('/togif', methods=['POST'])
def to_gif():
   return convertto_gif()

@app.route('/giftoimg', methods=['POST'])
def gif_to_img():
   return convertgif_toimg()

@app.route('/compressimg', methods=['POST'])
def img_compress():
   return compress_image()

@app.route('/compress', methods=['POST'])
def compresspdf():
    return compress_pdf()

@app.route('/convert', methods=['POST'])
def convert_to_pdf():
    return convert_pdf()

@app.route('/pdf/<user_id>')
def pdf_view(user_id):
    pdf_data = pdf_collection.find_one({"user_id": user_id})
    if pdf_data:
        pdf_binary_data = pdf_data["file"]
    else:
        return render_template("error.html",  error_msg='No file found on Database')
    response = Response(pdf_binary_data, content_type='application/pdf')
    response.headers['Content-Disposition'] = 'attachment; filename=pdf_file.pdf'
    return response

@app.route('/download/<user_id>')
def download(user_id):
    image_data = bgremoved_collection.find_one({'user_id': user_id})
    image_collection_data=image_collection.find_one({'user_id': user_id})
    if image_data:
        binary_image_data = image_data['image_data']
    elif image_collection_data:
        binary_image_data = image_collection_data['image_data']
    else:
        return render_template("error.html",  error_msg='No file found on Database')
    image = Image.open(io.BytesIO(binary_image_data))
    image_format = image.format
    response = make_response(binary_image_data)
    response.headers.set('Content-Type', 'image/'+ image_format)
    response.headers.set('Content-Disposition', 'attachment', filename=f'img{int(time.time())}.{image_format}')
    return response

@app.route('/result', methods=['POST'])
def upload_image():
    file = request.files.get('image')
    try:
        if file is None or file.filename == '':
            return 'No file was submitted or the file is empty'
        image = Image.open(file)
        if image.format == 'PNG':
            image = image.convert('RGB')
        user_id = generate_unique_id()
        img_io = io.BytesIO()
        image.save(img_io,format='JPEG',quality=100)
        img_io.seek(0)
        image_d = img_io.read()
        colorization_collection.insert_one({'user_id': user_id, 'image_data': image_d, 'type': 'original'})
        image_data = colorization_collection.find_one({'user_id': user_id,'type': 'original'})['image_data']
        image = Image.open(io.BytesIO(image_data))
        img_io = io.BytesIO()
        image.save(img_io,format='JPEG',quality=100)
        img_io.seek(0)
        img_str = base64.b64encode(img_io.getvalue()).decode()
        colorized_image_file = imgcolorize(image_d,user_id)
        return render_template("image.html", original=img_str, colored=colorized_image_file,user_id=user_id)
    except OSError:
         return render_template("error.html",error_msg='Upload a valid image file.')

@app.route('/save/<user_id>')
def save(user_id):
    try:
        image_data = base64.b64decode(colorization_collection.find_one({'user_id': user_id,'type': 'Colored'})['image_data'])
        image = Image.open(io.BytesIO(image_data))
        image_format = image.format
        response = make_response(image_data)
        response.headers.set('Content-Type', 'image/jpeg')
        response.headers.set('Content-Disposition', 'attachment', filename=f'img{int(time.time())}.jpeg')
        return response
    except:
        return render_template("error.html",  error_msg='No file found on Database')

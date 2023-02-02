import io
import threading
from flask import request, render_template
from PIL import Image, ImageFilter
from pymongo import MongoClient
import base64
import threading
from time import sleep
from utils import generate_unique_id

# Connect to MongoDB
# client = MongoClient("mongodb+srv://prabin:bprabin@cluster0.2phmxej.mongodb.net/test")
client = MongoClient("mongodb://localhost:27017")
db = client["imageLab"]
image_collection = db['Images']

def delete_image_collection(user_id):
    sleep(140) # wait for 2 minutes
    image_collection.delete_one({'user_id': user_id})

def image_processing(image, user_id, image_type,img_format,quality):
    img_io = io.BytesIO()
    image.save(img_io, format=img_format, quality=quality)
    img_io.seek(0)
    image_data = img_io.read()
    image_collection.insert_one({'user_id': user_id, 'image_data': image_data, 'type': image_type})
    threading.Thread(target=delete_image_collection, args=(user_id,)).start()
    image_data = image_collection.find_one({'user_id': user_id})['image_data']
    image = Image.open(io.BytesIO(image_data))
    img_io = io.BytesIO()
    image.save(img_io, format= img_format,quality=quality)
    img_io.seek(0)
    img_str = base64.b64encode(img_io.getvalue()).decode()
    return img_str

def handle_error(error_msg):
    return render_template("error.html", error_msg='Upload a valid image file.')

def view_result_Page(message,user_id,image_data,format):
    return render_template('result.html',message=message,user_id=user_id ,image_data=image_data,format=format)

def compress_image():
    file = request.files.get('cfile')
    try:
        if file is None or file.filename == '':
            return 'No file was submitted or the file is empty'
        image = Image.open(file)
        user_id = generate_unique_id()
        image = image.convert("RGB")
        img_str = image_processing(image, user_id, 'compress','JPEG',70)
        return view_result_Page("Image Compressed Successfully",user_id ,img_str,'JPEG')
    except OSError:
        return handle_error

def convert_to_jpg():
    file = request.files.get('file')
    try:
        if file is None or file.filename == '':
            return 'No file was submitted or the file is empty'
        image = Image.open(file)
        if image.format != 'PNG':
            return handle_error('Upload a PNG image file.')
        user_id = generate_unique_id()
        image = image.convert("RGB")
        img_str = image_processing(image, user_id, 'jpg_conversion','JPEG',100)
        return view_result_Page("Image Converted Successfully",user_id ,img_str,'JPEG')
    except OSError:
        return handle_error

def convert_to_png():
    file = request.files.get('jfile')
    try:
        if file is None or file.filename == '':
            return 'No file was submitted or the file is empty'
        image = Image.open(file)
        if image.format != 'JPEG':
            return render_template("error.html",error_msg='Upload a JPEG image file.')
        user_id = generate_unique_id()
        img_str = image_processing(image, user_id, 'png_conversion','PNG',100)
        return view_result_Page("Image Converted Successfully",user_id ,img_str,'PNG')
    except OSError:
        return handle_error

def convertgif_toimg():
    file = request.files.get('kfile')
    try:
        if file is None or file.filename == '':
            return 'No file was submitted or the file is empty'
        gif = Image.open(file)
        gif.seek(2)
        user_id = generate_unique_id()
        img_str = image_processing(gif, user_id, 'gif_to_image_conversion','PNG',100)
        return view_result_Page("GIF to Image conversion Successful",user_id ,img_str,'PNG')
    except:
        return handle_error
    
def convertto_gif():
    file = request.files.get('img')
    try:
        if file is None or file.filename == '':
            return 'No file was submitted or the file is empty'
        image = Image.open(file)
        user_id = generate_unique_id()
        img_str = image_processing(image, user_id, 'image_to_gif_conversion','GIF',100)
        return view_result_Page("GIF to Image conversion Successful",user_id ,img_str,'GIF')
    except:
        return handle_error
    
def convertto_art():
    file = request.files.get('sfile')
    try:
        if file is None or file.filename == '':
            return 'No file was submitted or the file is empty'
        image = Image.open(file)
        image = image.convert('L')
        image = image.filter(ImageFilter.CONTOUR)
        user_id = generate_unique_id()
        img_str = image_processing(image, user_id, 'sketch_conversion','JPEG',100)
        return view_result_Page("Image converted to pencil sketch Successfully",user_id ,img_str,'JPEG')
    except:
        return handle_error
    
def convertto_grayscale():
    file = request.files.get('gfile')
    try:
        if file is None or file.filename == '':
            return 'No file was submitted or the file is empty'
        image = Image.open(file)
        img_format=image.format
        image = image.convert('L')
        user_id = generate_unique_id()
        img_str = image_processing(image, user_id, 'grayscale_conversion',img_format,100)
        return view_result_Page("Grayscale conversion Successful",user_id ,img_str,img_format)
    except:
        return handle_error
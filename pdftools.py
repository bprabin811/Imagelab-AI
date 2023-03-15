from flask import render_template, request
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PIL import Image
from utils import generate_unique_id
from pymongo.errors import PyMongoError
from pymongo import MongoClient
from PyPDF2 import PdfReader, PdfWriter
import threading
from time import sleep

client = MongoClient("mongodb://localhost:27017")
# client = MongoClient("mongodb+srv://prabin:bprabin@cluster0.2phmxej.mongodb.net/test")
db = client["imageLab"]
pdf_collection = db["pdf_files"]

def handle_error(error_msg):
    return render_template("error.html", error_msg=error_msg)

def delete_pdf_collection(user_id):
    sleep(140) # wait for 2 minutes
    pdf_collection.delete_one({'user_id': user_id})

def save_to_mongodb(collection, user_id, binary_data, delete_func):
    try:
        collection.insert_one({"user_id": user_id, "file": binary_data})
        threading.Thread(target=delete_func, args=(user_id,)).start()
    except PyMongoError as e:
        return handle_error('Error occurred while trying to connect to MongoDB: {}'.format(e))

def convert_pdf():
    files = request.files.getlist('pfile')
    try:
        if not files or len(files) == 0:
            return handle_error('No file was submitted or the file is empty')

        pdf_buffer = BytesIO()
        pdf = canvas.Canvas(pdf_buffer, pagesize=A4)

        for file in files:
            try:
                image = Image.open(file)
                width, height = A4
                img_width, img_height = image.size
                if img_width > width or img_height > height:
                    ratio = min(width/img_width, height/img_height)
                    image = image.resize((int(img_width*ratio*0.95), int(img_height*ratio*0.95)), Image.Resampling.LANCZOS)
                    img_width, img_height = image.size

                x = (width - img_width) / 2
                y = (height - img_height) / 2

                pdf.drawInlineImage(image, x, y)
                pdf.showPage()
            except:
                return handle_error('Error occurred: Upload Valid Files.')

        pdf.save()
        pdf_buffer.seek(0)
        user_id = generate_unique_id()
        pdf_binary_data = pdf_buffer.getvalue()
        save_to_mongodb(pdf_collection, user_id, pdf_binary_data, delete_pdf_collection)
        return render_template('pdf.html', message="PDF Conversion Successful", user_id=user_id)
    except Exception as e:
        return handle_error('Error occurred: {}'.format(e))

def compress_pdf():
    file = request.files.get('cfile')
    try:
        if not file:
            return handle_error('No file was submitted or the file is empty')
        pdf_reader = PdfReader(file)
        pdf_writer = PdfWriter()
        for page in pdf_reader.pages:
            page.compress_content_streams()
            pdf_writer.add_page(page)
        user_id = generate_unique_id()
        compressed_file = BytesIO()
        pdf_writer.write(compressed_file)
        compressed_file.seek(0)
        save_to_mongodb(pdf_collection, user_id, compressed_file.read(), delete_pdf_collection)
        return render_template('pdf.html', message="PDF Compression Successful", user_id=user_id)
    except Exception as e:
        return handle_error('Error occurred: {}'.format(e))


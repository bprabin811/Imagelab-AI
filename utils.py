import uuid
import shutil
from time import sleep
import os

def generate_unique_id():
    return str(uuid.uuid4())

def delete_folder(folder_path):
    sleep(125)
    shutil.rmtree(folder_path)


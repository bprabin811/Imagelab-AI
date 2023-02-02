import uuid
import shutil
from time import sleep

def generate_unique_id():
    return str(uuid.uuid4())

def delete_folder(folder):
    # Wait for 1 minutes
    sleep(60)
    # Delete the folder
    shutil.rmtree(folder)


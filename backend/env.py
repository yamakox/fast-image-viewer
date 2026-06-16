from dotenv import load_dotenv
import os
import ast

load_dotenv()

# Django settings.py
DEBUG = ast.literal_eval(os.environ.get('DEBUG', 'False'))
HOST = os.environ.get('HOST', '127.0.0.1')
PORT = int(os.environ.get('PORT', '8000'))
WORKERS = int(os.environ.get('WORKERS', '4'))
ALLOWED_HOSTS = [x for x in os.environ.get('ALLOWED_HOSTS', 'localhost').split(';') if x]
STATIC_ROOT = os.environ.get('STATIC_ROOT', '/var/www/example.com/static/')
PAGINATION_SIZE = int(os.environ.get('PAGINATION_SIZE', '100'))
CORS_ALLOWED_ORIGINS = [x for x in os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:5173').split(';') if x]

# fast-image-viewer
FIV_APPDATA_FOLDER_PATH = os.environ.get('FIV_APPDATA_FOLDER_PATH', '/var/opt/fast-image-viewer')
FIV_DATASET_FOLDER_PATH = os.environ.get('FIV_DATASET_FOLDER_PATH', '/var/opt/fast-image-viewer/dataset')
FIV_THUMBNAIL_SIZE = int(os.environ.get('FIV_THUMBNAIL_SIZE', '100'))
FIV_THUMBNAIL_QUALITY = int(os.environ.get('FIV_THUMBNAIL_QUALITY', '70'))

from dotenv import load_dotenv
import os

load_dotenv()

DEBUG = eval(os.environ.get('DEBUG', 'False'))
FIV_APPDATA_FOLDER_PATH = os.environ.get('FIV_APPDATA_FOLDER_PATH', '/var/opt/fast-image-viewer')
FIV_DATASET_FOLDER_PATH = os.environ.get('FIV_DATASET_FOLDER_PATH', '/var/opt/fast-image-viewer/dataset')
FIV_THUMBNAIL_SIZE = eval(os.environ.get('FIV_THUMBNAIL_SIZE', '100'))
FIV_THUMBNAIL_QUALITY = eval(os.environ.get('FIV_THUMBNAIL_QUALITY', '70'))

import os
from dotenv import load_dotenv
load_dotenv()
random = os.urandom(24).hex()
WTF_CSRF_SECRET_KEY = os.getenv('WTF_CSRF_SECRET_KEY')
APP_SECRET_KEY = os.getenv('APP_SECRET_KEY')
# TEST_DB_URI = "sqlite:///./test.db"
PRODUCTION_DB_URI = os.getenv('PRODUCTION_DB_URI')
UPLOAD_FOLDER = "./uploads/contracts"
UPLOAD_FOLDER_ACTS = "./uploads/acts"
UPLOAD_FOLDER_ADDITIONS = "./uploads/additions"
PERCENTAGE_AMOUNT = 10

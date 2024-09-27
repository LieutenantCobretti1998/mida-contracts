import os
random = os.urandom(24).hex()
WTF_CSRF_SECRET_KEY = os.environ.get('CSRF_TOKEN')
APP_SECRET_KEY = os.environ.get('APP_KEY')
TEST_DB_URI = "sqlite:///./test.db"
UPLOAD_FOLDER = "./uploads/contracts"
UPLOAD_FOLDER_ACTS = "./uploads/acts"
UPLOAD_FOLDER_ADDITIONS = "./uploads/additions"
PERCENTAGE_AMOUNT = 10

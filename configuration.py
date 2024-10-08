import os
random = os.urandom(24).hex()
WTF_CSRF_SECRET_KEY = "9c0363e3c34ea893c8ee79993ec76d14a949a40bb38856fa"
APP_SECRET_KEY = "aa4d63eb7d674b54e0a144abb1d848691efc0efd7f20b4a5."
TEST_DB_URI = "sqlite:///./test.db"
PRODUCTION_DB_URI = "sqlite:///contracts.db"
UPLOAD_FOLDER = "./uploads/contracts"
UPLOAD_FOLDER_ACTS = "./uploads/acts"
UPLOAD_FOLDER_ADDITIONS = "./uploads/additions"
PERCENTAGE_AMOUNT = 10

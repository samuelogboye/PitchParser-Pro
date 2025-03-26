import os 

ALLOWED_EXTENSIONS = {'pdf', 'pptx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_upload_folder():
    upload_folder = os.getenv('UPLOAD_FOLDER')
    # Check if the directory exists, if not, create it
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    return upload_folder
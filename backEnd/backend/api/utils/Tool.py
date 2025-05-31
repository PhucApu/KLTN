import os
from django.conf import settings

def fileToFile(fileName, filepath, new_file_ext):
    file_ext = os.path.splitext(fileName)[1].lower()
    if (file_ext not in new_file_ext):
        filepath = filepath.replace(file_ext, new_file_ext)
    return os.path.join(settings.MEDIA_ROOT,filepath) 
   
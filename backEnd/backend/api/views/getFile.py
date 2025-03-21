from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from ..models.upFile import UpFile

def get_pdf(request, file_id=4):
    pdf_file = get_object_or_404(UpFile, id=file_id)
    

    return FileResponse(pdf_file.file.open('rb'), content_type='application/pdf')

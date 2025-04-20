from django.urls import path
from api.views.getFile import get_pdf
from .views import upFileViews
from api.views.upFileViews import FileUploadView

urlpatterns = [
    path('upload', FileUploadView.as_view(), name='file-upload'),
    path('files/<int:file_id>/', get_pdf, name='get-pdf'),
]

import magic #pip install python-magic
from rest_framework.views import APIView
from ..models.component import component 
from rest_framework.response import Response 
from rest_framework.parsers import MultiPartParser, FormParser 
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from ..utils.Neo4jSp import remove_descendants_from_relationships
from ..utils.neo4j_driver import driver
from django.http import JsonResponse
from ..models.file import file

# from ..models.file import UpFile
from ..serializers.upFileSerializer import UpFileSerializer

class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)  # Cho phép xử lý file upload

    def post(self, request, *args, **kwargs):
    
        file_serializer = UpFileSerializer(data=request.data)
        
        if file_serializer.is_valid():
            file_serializer.save()  # Lưu file vào database
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

      
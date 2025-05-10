
from rest_framework.views import APIView

from rest_framework.response import Response 
from rest_framework.parsers import MultiPartParser, FormParser 
from rest_framework import status


from ..permissions.permission import IsAdmin
# from ..models.file import UpFile
from ..serializers.upFileSerializer import UpFileSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication


class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)  # Cho phép xử lý file upload
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
    
        file_serializer = UpFileSerializer(data=request.data)
        
        if file_serializer.is_valid():
            file_serializer.save()  # Lưu file vào database
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

      
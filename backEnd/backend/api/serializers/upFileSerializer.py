from rest_framework import serializers
from ..models.file import file

class UpFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = file
        fields = ['id', 'file','status', 'name', 'upFile_at'] 

    def validate_file(self, value):
        """Kiểm tra định dạng file upload"""
        allowed_extensions = ['doc', 'docx','pdf']
        file_extension = value.name.split('.')[-1].lower()
        
        if f"{file_extension}" not in allowed_extensions:
            raise serializers.ValidationError("Chỉ chấp nhận file Word (docx, doc)")
        
        return value

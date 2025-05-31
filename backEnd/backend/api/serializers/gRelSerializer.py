from rest_framework import serializers
from ..models.gRel import gRel

class gRelSerializer(serializers.ModelSerializer):
    class Meta:
        model = gRel
        # fields = ['id', 'idLaw','parent','child','descendants','name','content','contentSearch','is_shorten','is_theory']
        fields = '__all__'
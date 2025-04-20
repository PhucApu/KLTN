from rest_framework import serializers
from ..models.gConc import GConc

class gConcSerializer(serializers.ModelSerializer):
    class Meta:
        model = GConc
        # fields = ['id', 'idLaw','parent','child','descendants','name','content','contentSearch','is_shorten','is_theory']
        fields = '__all__'
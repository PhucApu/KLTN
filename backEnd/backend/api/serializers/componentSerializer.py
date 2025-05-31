from rest_framework import serializers
from ..models.component import component

class componentSerializer(serializers.ModelSerializer):
    class Meta:
        model = component
        # fields = ['id', 'idLaw','parent','child','descendants','name','content','contentSearch','is_shorten','is_theory']
        fields = '__all__'

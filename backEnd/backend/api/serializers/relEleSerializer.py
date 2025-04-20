from rest_framework import serializers
from ..models.relEle import relEle

class relEleSerializer(serializers.ModelSerializer):
    class Meta:
        model = relEle
        # fields = ['id', 'idLaw','parent','child','descendants','name','content','contentSearch','is_shorten','is_theory']
        fields = '__all__'
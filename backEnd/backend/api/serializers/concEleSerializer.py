from rest_framework import serializers
from ..models.concEle import Concele

class concEleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concele
        # fields = ['id', 'idLaw','parent','child','descendants','name','content','contentSearch','is_shorten','is_theory']
        fields = '__all__'
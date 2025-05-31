from rest_framework import serializers
from ..models.gText import Gtext

class gTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gtext
        # fields = ['id', 'idLaw','parent','child','descendants','name','content','contentSearch','is_shorten','is_theory']
        fields = '__all__'

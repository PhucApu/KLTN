from rest_framework import serializers
from ..models.suggertRel import SuggestRel

class SuggestRelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuggestRel
        # fields = ['id', 'idLaw','parent','child','descendants','name','content','contentSearch','is_shorten','is_theory']
        fields = '__all__'
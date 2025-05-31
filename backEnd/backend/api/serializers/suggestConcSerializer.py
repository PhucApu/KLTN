from rest_framework import serializers
from ..models.suggestConc import SuggestConc

class SuggestConcSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuggestConc
        # fields = ['id', 'idLaw','parent','child','descendants','name','content','contentSearch','is_shorten','is_theory']
        fields = '__all__'
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from rest_framework.decorators import api_view
from django.http import JsonResponse
from ..models.file import file
from ..models.relEle import relEle
from itertools import combinations
from ..models.suggertRel import SuggestRel
from ..utils.suggest import get_unseen_pairs
from ..utils.synonyms import synonyms
from ..serializers.relEleSerializer import relEleSerializer


@csrf_exempt
@api_view(['GET'])
def init_suggestrelation(request, idLaw, idSuggest):
    try:
        fileItem = file.objects.get(id=idLaw)
        relEleItem = relEle.objects.filter(IdLaw = idLaw)
        if not relEleItem.exists():
            return JsonResponse({"message": 'Các bước trước chưa được thực hiện'}, status=400)
    except:
        return JsonResponse({"message": 'Các bước trước chưa được thực hiện'}, status=400)
        
    if SuggestRel.objects.filter(id1=idSuggest).exists():
        return JsonResponse({"message": 'Thành công'}, status=200)
    if SuggestRel.objects.filter(id2=idSuggest).exists():
        return JsonResponse({"message": 'Thành công'}, status=200)

    id_list =list(relEle.objects.values_list('id',flat=True))
    id_pairs = list(map(list, combinations(id_list, 2)))
    exit_id_list = list(SuggestRel.objects.values('id1','id2'))
    exit_id_list = [[row['id1'], row['id2']] for row in exit_id_list]
    not_exit_id_list = get_unseen_pairs(id_pairs,exit_id_list)
    for item in not_exit_id_list:
        SuggestRel.objects.create(
            id1=relEle.objects.get(id=item[0]),
            id2=relEle.objects.get(id=item[1]),
            relation1 = relEle.objects.filter(id=item[0]).first().relation,
            relation2 = relEle.objects.filter(id=item[1]).first().relation,
            similar_index = synonyms(),
        )
    return JsonResponse({"message": 'Thành công'}, status=200)
    
@csrf_exempt
@api_view(['POST'])
def get_suggest_rel(request):
    data=request.data
    filter1 = SuggestRel.objects.filter(id1_id = data.get('id'), relation1__icontains = data.get('rel'))
    filter2 = SuggestRel.objects.filter(id2_id = data.get('id'), relation2__icontains = data.get('rel'))
    combined = (filter1 | filter2).distinct()

    serializer = relEleSerializer(combined, many=True)

    return JsonResponse(serializer.data, status=200)
    

        

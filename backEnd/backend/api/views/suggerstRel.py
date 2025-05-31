from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
from ..models.file import file
from ..models.relEle import relEle
from itertools import combinations
from ..models.suggertRel import SuggestRel
from ..utils.suggest import get_unseen_pairs
from ..utils.synonyms import synonyms
from ..serializers.relEleSerializer import relEleSerializer
from ..permissions.permission import IsSuperAdmin
from ..permissions.permission import IsAdmin
from ..utils.Wraps import before_and_after_view


@permission_classes([IsAdmin])  
@api_view(['GET'])
@before_and_after_view(number=1)
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
        relation11 = relEle.objects.filter(id=item[0]).first().relation
        relation22 = relEle.objects.filter(id=item[1]).first().relation
        SuggestRel.objects.create(
            id1=relEle.objects.get(id=item[0]),
            id2=relEle.objects.get(id=item[1]),
            relation1 = relation11,
            relation2 = relation22,
            similar_index = synonyms(text1=relation11,text2=relation22),
        )
    return JsonResponse({"message": 'Thành công'}, status=200)
    
@permission_classes([IsAdmin])  
@api_view(['POST'])
def get_suggest_rel(request):
    data=request.data
    try:
        idlaw = relEle.objects.filter(id=data.get("id")).first().IdLaw
        filter1 = SuggestRel.objects.filter(id1_id = data.get('id'), relation2__icontains = data.get('rel'),id1__IdLaw = idlaw,id2__IdLaw = idlaw).values("id2","relation2","similar_index")
        filter2 = SuggestRel.objects.filter(id2_id = data.get('id'), relation1__icontains = data.get('rel'),id1__IdLaw = idlaw,id2__IdLaw = idlaw).values("id1","relation1","similar_index")
        filter1 = [{"id":item["id2"],"relation":item["relation2"], "similar": item["similar_index"]} for item in filter1]
        filter2 = [{"id":item["id1"],"relation":item["relation1"], "similar": item["similar_index"]} for item in filter2]
        combine = [dict(t) for t in {tuple(d.items()) for d in (filter1 + filter2)}]
        combine.sort(key=lambda x: x['similar'], reverse=True)
        return JsonResponse(combine,safe=False, status=200)
    except:
        return JsonResponse({"message": "Truyền đầy đủ coi"}, status=200)

        

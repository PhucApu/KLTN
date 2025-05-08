from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from rest_framework.decorators import api_view
from django.http import JsonResponse

from ..models.relEle import relEle
from ..models.file import file
from ..models.concEle import Concele
from itertools import combinations
from ..models.suggestConc import SuggestConc
from ..utils.suggest import get_unseen_pairs
from ..utils.synonyms import synonyms
from ..models.concEle import Concele
from ..serializers.suggestConcSerializer import SuggestConcSerializer

@csrf_exempt
@api_view(['GET'])
def init_suggestconc(request, idLaw, idSuggest):
    try:
        fileItem = file.objects.get(id=idLaw)
        ConceleItem = Concele.objects.filter(IdLaw = idLaw)
        if not ConceleItem.exists():
            return JsonResponse({"message": 'Các bước trước chưa được thực hiện'}, status=400)
    except:
        return JsonResponse({"message": 'Các bước trước chưa được thực hiện'}, status=400)
        
    if SuggestConc.objects.filter(id1_id=idSuggest).exists():
        return JsonResponse({"message": 'Thành công'}, status=200)
    if SuggestConc.objects.filter(id2_id=idSuggest).exists():
        return JsonResponse({"message": 'Thành công'}, status=200)
    try:
        id_list =list(Concele.objects.values_list('id',flat=True))
        id_pairs = list(map(list, combinations(id_list, 2)))
        exit_id_list = list(SuggestConc.objects.values('id1','id2'))
        exit_id_list = [[row['id1'], row['id2']] for row in exit_id_list]
        not_exit_id_list = get_unseen_pairs(id_pairs,exit_id_list)
        print('sai')
        for item in not_exit_id_list:
            print(item)
            SuggestConc.objects.create(
                id1=Concele.objects.get(id=item[0]),
                id2=Concele.objects.get(id=item[1]),
                conc1 = Concele.objects.filter(id=item[0]).first().conC,
                conc2 = Concele.objects.filter(id=item[1]).first().conC,
                similar_index = synonyms(),
            )
    except Exception as e:
            print(e)
            return JsonResponse({"message": 'Thất bại'}, status=400)

    return JsonResponse({"message": 'Thành công'}, status=200)
    
    
@csrf_exempt
@api_view(['POST'])
def get_suggest_conc(request):
    data=request.data
    try:
        idlaw = Concele.objects.filter(id=data.get("id")).first().IdLaw
        filter1 = SuggestConc.objects.filter(id1_id = data.get('id'), conc2__icontains = data.get('conc'),id1__IdLaw = idlaw,id2__IdLaw = idlaw).values("id2","conc2","similar_index")
        filter2 = SuggestConc.objects.filter(id2_id = data.get('id'), conc1__icontains = data.get('conc'),id2__IdLaw = idlaw,id1__IdLaw = idlaw).values("id1","conc1","similar_index")
        filter1 = [{"id":item["id2"],"conc":item["conc2"], "similar": item["similar_index"]} for item in filter1]
        filter2 = [{"id":item["id1"],"conc":item["conc1"], "similar": item["similar_index"]} for item in filter2]
        combine = [dict(t) for t in {tuple(d.items()) for d in (filter1 + filter2)}]
        combine.sort(key=lambda x: x['similar'], reverse=True)
        return JsonResponse(combine,safe=False, status=200)
    except:
        return JsonResponse({"message": "Truyền đầy đủ coi"}, status=200)

    
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from rest_framework.decorators import api_view
from django.http import JsonResponse
from ..models.file import file
from ..models.relEle import relEle
from ..models.gRel import gRel
from ..models.suggertRel import SuggestRel
from rest_framework.response import Response
from ..serializers.gRelSerializer import gRelSerializer
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models.expressions import RawSQL
from django.db.models import Max



@csrf_exempt
@api_view(['POST'])
def init_gRel(request):
    data=request.data
    try:
        fileitem = file.objects.get(id=data.get('idLaw'))
    except:
        return JsonResponse({"message": 'Các thao tác trước chưa được xử lý'}, status=400)
    relEleLstItem = relEle.objects.filter(IdLaw = data.get('idLaw'))
    
    if not relEleLstItem.exists():
            return JsonResponse({"message": 'Các thao tác trước chưa được xử lý'}, status=400)
    
    gRelLstItem = gRel.objects.filter(lstidlaw__contains=[data.get('IdLaw')])
      
    if gRelLstItem.exists():
        return JsonResponse({"message": 'Thành công'}, status=200)
    with transaction.atomic():
        try:
            for conceleItem in relEleLstItem:
                item = gRel.objects.filter(id=conceleItem.similar).first()
                if item:    
                    item.lstRel.append(conceleItem.relation)
                    item.lstidlaw.append(conceleItem.IdLaw.id)
                    item.meaning if item.meaning else conceleItem.Meaning
                    item.descendants.append(conceleItem.descendants)
                    item.lstgConcO.append(conceleItem.concO.id)
                    item.lstgConcS.append(conceleItem.concS.id)
                    item.update_concs.append(conceleItem.concS.id)
                    item.update_conco.append(conceleItem.concO.id)
                    item.updaterel = 1
                    item.save()
                else:
                    kwargs = {
                        'lstidlaw': [conceleItem.IdLaw.id],
                        'lstRel': [conceleItem.relation],
                        'meaning': conceleItem.Meaning,
                        'descendants': conceleItem.descendants,
                        'lstgConcS': [conceleItem.concS.id],
                        'lstgConcO': [conceleItem.concO.id],
                        'update_concs': [conceleItem.concS.id],
                        'update_conco': [conceleItem.concO.id],
                    }
                    si = conceleItem.similar
                    if si:
                        kwargs['id'] = si
                    
                    newgrel = gRel.objects.create(**kwargs)
                    conceleItem.similar = newgrel.id 
                    conceleItem.save()
        except Exception as e:
            print(e)
            return JsonResponse({"message": 'Lỗi tạo thực thể'}, status=400)

    return JsonResponse({"message": 'Thành công'}, status=200)

@csrf_exempt
@api_view(['GET'])
def search_grel(request):
    try:
        # Lấy các tham số tìm kiếm từ query string
        data = request.data
        keyword = data.get('meaning')
        lawid = data.get('lawid')
        gconcs = data.get('gconcs')  
        gconco = data.get('gconco')
        rel = data.get('rel')

        # Xây dựng bộ lọc
        queryset = gRel.objects.all()
        if rel:
            queryset = queryset.annotate(
            match=RawSQL(
            "JSON_SEARCH(LOWER(lstRel), 'all', LOWER(%s)) IS NOT NULL",
            [f"%{rel}%"]
            )
            ).filter(match=True)

        if keyword:
            queryset = queryset.filter(meaning__icontains=keyword)

        if lawid:
            queryset = queryset.filter(lstidlaw__contains=[lawid])

        if gconcs:
            for item in gconcs:
                queryset = queryset.filter(lstgConcS__contains=[item])

        if gconco:
            for item in gconco:
                queryset = queryset.filter(lstgConcO__contains=[item])

        # Trả về danh sách JSON
        results = []
        for item in queryset:
            results.append({
                "id": item.id,
                "meaning": item.meaning,
                "lstidlaw": item.lstidlaw,
                "lstRel": item.lstRel,
                "descendants": item.descendants,
                "lstgConcS": item.lstgConcS,
                "lstgConcO": item.lstgConcO,
            })

        return Response(results, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])
def suggest_gRel2(request):
    data = request.data 
    rela = data.get('relation')
    id = data.get('id')
    result = list()
    lstgrel = gRel.objects.all()
    similar = SuggestRel.objects.all()
    if id:
        similar1 = similar.filter(id1_id=id).values('relation2','similar_index')
        similar2 = similar.filter(id2_id=id).values('relation1','similar_index')
    else:
        return JsonResponse({'message': "Không truyền id"},status = 400)
    similar = {}
    if similar1:
        for item in similar1:
            similar[item['relation2']] = item['similar_index']
    if similar2:
        for item in similar2:
            similar[item['relation1']] = item['similar_index']
    if rela:
        lstgrel = lstgrel.annotate(
            match=RawSQL(
            "JSON_SEARCH(lstRel, 'all', %s) IS NOT NULL",
            [f"%{rela}%"]
            )
            ).filter(match=True)
    # similar2 = similar2.annotate(
    #         match=RawSQL(
    #         "JSON_SEARCH(lstConC, 'all', %s) IS NOT NULL",
    #         [f"%{rela}%"]
    #         )
    #         ).filter(match=True)
    
    for grel in lstgrel:
        max_similar = 0
        for key,value in similar.items():
            if key in grel.lstRel and max_similar < value:
                max_similar = value
        result.append({'object': gRelSerializer(grel).data, 'similar': max_similar})
    result.sort(key=lambda x: x['similar'], reverse=True)
    return JsonResponse(result,safe=False,status = 200)
    
@csrf_exempt
@api_view(['PUT'])
def update_grel(request, grel_id):
    grel = get_object_or_404(gRel, id=grel_id)
    try:
        # grel.lstidlaw = request.data.get('lstidlaw', grel.lstidlaw)
        grel.lstRel = request.data.get('lstRel', grel.lstRel)
        grel.meaning = request.data.get('meaning', grel.meaning)
        # grel.descendants = request.data.get('descendants', grel.descendants)
        # grel.lstgConcS = request.data.get('lstgConcS', grel.lstgConcS)
        # grel.lstgConcO = request.data.get('lstgConcO', grel.lstgConcO)
        # grel.update_concs = request.data.get('update_concs', grel.update_concs)
        # grel.update_conco = request.data.get('update_conco', grel.update_conco)
        grel.updaterel = 1
        grel.save()
        return Response({"message": "Thành công"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@csrf_exempt
@api_view(['POST'])
def update_similar_rel(request):
    data = request.data.get('lst')
    if not isinstance(data, list):
        return JsonResponse({"message": "request là một list."}, status=400)
    elif not data:
        return JsonResponse({"message": "request rỗng"}, status=400)
    data= set(data)
    similar = set()
    groub_similar = dict()
    for item in data:
        conceptitem = relEle.objects.filter(id = item).values_list("relation","similar")
        if not conceptitem:
            return JsonResponse({"message": "id không tồn tại"}, status=400)
        if conceptitem:
             similar.add(conceptitem)
    for conC1, similar_index in similar:
        if similar:
            gr = None
        else:
            gr = gRel.objects.filter(id=similar_index)
        if gr:
             groub_similar[similar_index] = f"{groub_similar.get(similar_index,"")+ "," if similar_index in groub_similar else ""}{conC1}"
    
    len_groub_similar = len(groub_similar)
    if len_groub_similar  > 1:
         list_conc = [value for key,value in groub_similar ]
         return JsonResponse({"message": f"các phần tử {list_conc} thuộc {len_groub_similar} khác nhau"}, status=401)
    if len_groub_similar == 1:
        similar_index = groub_similar.keys()[0]
        for item in data: 
            gRel.objects.filter(id=item).update(similar=similar_index)
    if len_groub_similar == 0:
        update_similar = relEle.objects.aggregate(Max('similar'))['similar__max']
        for item in data:
            relEle.objects.filter(id=item).update(similar = update_similar)
    return JsonResponse({"message": f"thành công {data}"},status=200)
    
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from rest_framework.decorators import api_view
from django.http import JsonResponse
from ..models.file import file
from ..models.concEle import Concele
from ..models.gConc import GConc
from ..models.concEle import Concele
from rest_framework.response import Response
from rest_framework import status
from ..serializers.gConcSerializer import gConcSerializer
from ..models.suggestConc import SuggestConc
from django.db.models.expressions import RawSQL


# Khỏi tạo gConc => trả về thành công 200, không thành công 400
@csrf_exempt
@api_view(['POST'])
def init_gConc(request):
    data=request.data
    try:
        fileitem = file.objects.get(id=data.get('idLaw'))
    except:
        return JsonResponse({"message": 'Các thao tác trước chưa được xử lý'}, status=400)
    conceleLstItem = Concele.objects.filter(idLaw = data.get('idLaw'))
    
    if not conceleLstItem.exists():
            return JsonResponse({"message": 'Các thao tác trước chưa được xử lý'}, status=400)
    
    gConcLstItem = GConc.objects.filter(lstidlaw__contains=[data.get('IdLaw')])
      
    if gConcLstItem.exists():
        return JsonResponse({"message": 'Thành công'}, status=200)
    with transaction.atomic():
        try:
            for conceleItem in conceleLstItem:
                item = GConc.objects.filter(id=conceleItem.similar).first()
                if item:
                    item.lstConC = item.lstConC + conceleItem.conC
                    item.lstidlaw = item.lstidlaw + conceleItem.IdLaw
                    item.meaning = item.meaning if item.meaning else conceleItem.Meaning
                    item.descendants = item.descendants + conceleItem.descendants
                    item.updateNeo4j = 2
                    item.save()
                else:
                    GConc.objects.create(
                        id = conceleItem.similar,
                        lstidlaw = [conceleItem.IdLaw],
                        lstConC = [conceleItem.conC],
                        meaning = conceleItem.Meaning,
                        descendants = conceleItem.descendants
                    )
        except:
            return JsonResponse({"message": 'Lỗi tạo thực thể'}, status=400)

    return JsonResponse({"message": 'Thành công'}, status=200)





# Lấy danh sách hoặc tìm kiếm theo meaning, idLaw trong lstidlaw, conc trong lstconc
@csrf_exempt
@api_view(['GET'])
def get_gconc_list(request):
    meaning = request.data.get('meaning', None)    
    idlaw = request.data.get('idlaw', None)    
    conc = request.data.get('conc', None)      

    queryset = GConc.objects.all()
    if conc:
            queryset = queryset.annotate(
            match=RawSQL(
            "JSON_SEARCH(lstConC, 'all', %s) IS NOT NULL",
            [f"%{conc}%"]
            )
            ).filter(match=True)

    if meaning:
            queryset = queryset.filter(meaning__icontains=meaning)

    if idlaw:
            queryset = queryset.filter(lstidlaw__contains=[idlaw])

        
    results = []
    for item in queryset:
            results.append({
                "id": item.id,
                "meaning": item.meaning,
                "lstidlaw": item.lstidlaw,
                "lstConc": item.lstConC,
                "descendants": item.descendants,
                
            })

    return Response(results, status=status.HTTP_200_OK)


# Lấy chi tiết 1 bản ghi GConc
@csrf_exempt
@api_view(['GET'])
def get_gconc_detail(request, pk):
    try:
        gconc = GConc.objects.get(pk=pk)
        serializer = gConcSerializer(gconc)
        return Response(serializer.data)
    except GConc.DoesNotExist:
        return Response({'message': 'Không tìm thấy'}, status=status.HTTP_400_BAD_REQUEST)

# Tạo mới GConc
@csrf_exempt
@api_view(['POST'])
def create_gconc(request):
    serializer = gConcSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Cập nhật GConc
@csrf_exempt
@api_view(['PUT'])
def update_gconc(request, gconc_id):
    try:
        gconc = GConc.objects.get(id=gconc)
    except GConc.DoesNotExist:
        return Response({'message': 'Không tìm thấy'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = gConcSerializer(gconc, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Xoá GConc
@csrf_exempt
@api_view(['DELETE'])
def delete_gconc(request, pk):
    try:
        gconc = GConc.objects.get(pk=pk)
        gconc.delete()
        return Response({'message': 'Xóa thành công'}, status=status.HTTP_400_BAD_REQUEST)
    except GConc.DoesNotExist:
        return Response({'message': 'Không tìm thấy'}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])
def suggest_gconc(request):
    data = request.data 
    rela = data.get('conc')
    id = data.get('id')
    result = list()
    lstgrel = GConc.objects.all()
    similar1 = SuggestConc.objects.filter(id1_id=id).values('conc2','similar_index')
    
    similar2 = SuggestConc.objects.filter(id2_id=id).values('conc1','similar_index')
    similar1 = similar1.annotate(
            match=RawSQL(
            "JSON_SEARCH(lstConC, 'all', %s) IS NOT NULL",
            [f"%{rela}%"]
            )
            ).filter(match=True)
    similar2 = similar2.annotate(
            match=RawSQL(
            "JSON_SEARCH(lstConC, 'all', %s) IS NOT NULL",
            [f"%{rela}%"]
            )
            ).filter(match=True)
    similar = {}

    for item in similar1:
        similar[item['conc1']] = item['similar_index']

    for item in similar2:
        similar[item['conc2']] = item['similar_index']
    for grel in lstgrel:
        max_similar = 0
        for key,value in similar.items():
            if key in grel.lstConC:
                max_similar = value
        result.append({'object': grel, 'similar': max_similar})
    return JsonResponse(result,safe=False,status = 200)
    
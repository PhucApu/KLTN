
from django.views.decorators.csrf import csrf_exempt
from ..models.file import file 
from django.db.models import Q
from django.db import transaction
from rest_framework.views import APIView
from ..serializers.gTextSerializer import gTextSerializer
from ..models.gText import Gtext
from ..models.component import component
from ..models.file import file

from ..utils.textToGText import textToGText
from rest_framework.decorators import api_view
from django.http import JsonResponse

@csrf_exempt
@api_view(['POST'])
def create_gtext(request):
    serializer = gTextSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse({'message': 'Thêm mới thành công', 'data': serializer.data}, status=200)
    return JsonResponse(serializer.errors, status=400)

@csrf_exempt
@api_view(['PUT'])
def update_gtext(request, id):
    try:
        gtext = Gtext.objects.get(id=id)
    except Gtext.DoesNotExist:
        return JsonResponse({'message': 'Không tìm thấy gtext'}, status=400)
    
    serializer = gTextSerializer(gtext, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse({'message': 'Cập nhật thành công', 'data': serializer.data}, status = 200)
    return JsonResponse(serializer.errors, status=400)

@api_view(['DELETE'])
@csrf_exempt
def delete_gtext(request, id):
    try:
        gtext = Gtext.objects.get(id=id)
        gtext.delete()
        return JsonResponse({'message': 'Xóa thành công'}, status=200)
    except Gtext.DoesNotExist:
        return JsonResponse({'message': 'Không tìm thấy gtext'}, status=400)
    
@api_view(['GET'])
@csrf_exempt
def search_gtext(request):
    query = request.GET.get('q', '')  # Lấy tham số tìm kiếm từ query string
    if not query:
        return JsonResponse({'error': 'Query parameter "q" is required'}, status=400)
    
    results = Gtext.objects.filter(content__icontains=query)  # Tìm kiếm trong trường 'content'
    serializer = gTextSerializer(results, many=True)
    return JsonResponse(serializer.data)


@csrf_exempt
@api_view(['GET'])
def init_gtext(request, idLaw):
    try:
        fileitem = file.objects.get(id=idLaw)
        gtext = Gtext.objects.filter(idLaw = idLaw)
        componentItem = component.objects.filter(idLaw=idLaw)
        if not componentItem.exists():  # Kiểm tra nếu QuerySet rỗng
            return JsonResponse({'message': 'Không tìm thấy component tương ứng'}, status=400)
        
        if not gtext.exists():
                with transaction.atomic():
                    for item in componentItem:
                        if not item.content:
                            continue
                        trip = textToGText(item.content)
                        for itemTrip in trip:
                            Gtext.objects.create(
                                idLaw=item.idLaw,
                                descendants=item.descendants,  # Nếu là JSONField
                                content=item.content,
                                ConcS= itemTrip[0],
                                Relation= itemTrip[1],
                                ConcO=itemTrip[2]
                            )
    except :
        return JsonResponse({'message': 'Không tồn tại file tương ứng'}, status = 400)
    serializer = gTextSerializer(Gtext.objects.filter(idLaw = idLaw), many=True)
    # if serializer.is_valid():
        # serializer.save()
    return JsonResponse(serializer.data, safe=False)
    # return JsonResponse({'message': 'Lỗi gì rồi'}, status=400)

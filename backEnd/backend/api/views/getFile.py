from django.http import FileResponse, Http404
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ..models.file import file
from ..serializers.upFileSerializer import UpFileSerializer
import json
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from ..utils.neo4j_driver import driver
from ..models.component import component
from rest_framework.decorators import api_view, permission_classes
from ..utils.Neo4jSp import remove_descendants_from_relationships
from ..models.gConc import GConc
from ..permissions.permission import IsSuperAdmin
from ..permissions.permission import IsAdmin
from ..utils.Wraps import before_and_after_view



def get_pdf(request, file_id):
    pdf_file = get_object_or_404(file, id=file_id)
    

    return FileResponse(pdf_file.file.open('rb'), content_type='application/pdf')


@permission_classes([IsAdmin])  
def getFile(request):
    query_params = json.loads(request.body)
    search_filters = Q()
    filters = []
    filters = []
    if 'id' in query_params:
        filters.append(Q(id=query_params.get('id')))
    if 'name' in query_params:
        filters.append(Q(name__icontains=query_params.get('name')))
    if 'status' in query_params:
        filters.append(Q(status__icontains=query_params.get('status')))
    if 'upFile_at' in query_params:
        filters.append(Q(upFile_at__icontains=query_params.get('upFile_at')))
    
    if filters:
        search_filters = filters.pop()
        if query_params.get('isor') == 1:
            for f in filters:
                search_filters |= f
        elif query_params.get('isor') == 0:
            for f in filters:
                search_filters &= f
    components = file.objects.filter(search_filters)
    serializer = UpFileSerializer(components, many=True)
    
    return JsonResponse(serializer.data, status=200, safe=False)


@permission_classes([IsAdmin])  
@api_view(['POST'])
def dele_file(request,id):
    # data = request.data
    descendants_des = component.objects.filter(idLaw = id).values_list('id', flat=True)
    Flat = GConc.objects.filter(lstidlaw__contains = [id])
    print(Flat,descendants_des)
    if not Flat.exists() and  not descendants_des.exists():
        try:
            objectfile = file.objects.get(id = id)
        except:
            return JsonResponse({"message": 'File không tồn tại'}, status=200)

        objectfile.is_use = False
        objectfile.save()
        return JsonResponse({"message": 'Thành công'}, status=200)
        
    try:
        remove_descendants_from_relationships(driver=driver,descendants_des=descendants_des)
        objectfile = file.objects.get(id = id)
        objectfile.is_use = 0
        objectfile.save()
    except:
            return JsonResponse({"message": 'Xóa thất bại'}, status=400)
    return JsonResponse({"message": 'Thành công'}, status=200)



@permission_classes([IsAdmin])  
@api_view(['POST'])
def updateuse(request, id, number):
    item = file.objects.filter(id=id)
    if item.exists():
        fileitem = item.first().is_use
        if fileitem == bool(number):
            return False
        else:
            fileitem = number
            fileitem.save()
        return True
    return False

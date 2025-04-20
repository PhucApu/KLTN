from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from ..models.file import file 
from django.db.models import Q
from django.db import transaction
from rest_framework.views import APIView
from ..serializers.componentSerializer import componentSerializer
from ..models.component import component
from ..utils.parseLawStructure import parse_law_structure
from ..utils.isShorten import is_shorten
from ..utils.isTheory import is_theory
from rest_framework.decorators import api_view


@csrf_exempt
def process_pdf(request):
    data = json.loads(request.body)
    file_id = data.get("id")
    try:
        Flag = component.objects.get(id = file_id)
    except Exception as e:
        Flag = None
    if Flag == None:
        try:
            nodes, file_obj = parse_law_structure(file_id)
            with transaction.atomic():
                print('lỗi khi thêm')
                for index, row in nodes.iterrows():
                        print(index)
                        component.objects.create(
                        id = row['id'],
                        name = row['name'],
                        parent = row['parent'],
                        child = row['child'],
                        content = row['content'],
                        contentSearch = row['content'],
                        descendants = row['descendants'],
                        idLaw = file_obj,
                        is_shorten = 0, #is_shorten(row['content']),
                        is_theory = is_theory(row['content']),
                        )
        except Exception as e:
            print(e)
            return JsonResponse({"message": "Lỗi trong qua trình xử lý"}, status=400)
    
    lstItem = component.objects.filter(idLaw = file_id) 
    # print(lstItem)
    listCatalogue = componentSerializer(lstItem, many=True)
    return JsonResponse(listCatalogue.data, status=200, safe=False)


@csrf_exempt
def search_components(request):
    query_params = json.loads(request.body)
    search_filters = Q()

    # Lọc theo các tham số tìm kiếm
    filters = []
    if 'id' in query_params:
        filters.append(Q(id=query_params.get('id')))
    if 'idLaw' in query_params:
        filters.append(Q(idLaw=query_params.get('idLaw')))
    if 'parent' in query_params:
        filters.append(Q(parent=query_params.get('parent')))
    if 'name' in query_params:
        filters.append(Q(name__icontains=query_params.get('name')))
    if 'child' in query_params:
        filters.append(Q(child__icontains=query_params.get('descendants')))
    if 'descendants' in query_params:
        filters.append(Q(descendants__icontains=query_params.get('descendants')))
    if 'content' in query_params:
        filters.append(Q(content__icontains=query_params.get('content')))
    if 'contentSearch' in query_params:
        filters.append(Q(contentSearch__icontains=query_params.get('contentSearch')))
    if 'is_shorten' in query_params:
        filters.append(Q(is_shorten=query_params.get('is_shorten').lower() == 'true'))
    if 'is_theory' in query_params:
        filters.append(Q(is_theory=query_params.get('is_theory').lower() == 'true'))

    if filters:
        search_filters = filters.pop()
        if query_params.get('isor') == 1:
            for f in filters:
                search_filters |= f
        elif query_params.get('isor') == 0:
            for f in filters:
                search_filters &= f
    components = component.objects.filter(search_filters)
    serializer = componentSerializer(components, many=True)
    
    return JsonResponse(serializer.data, status=200, safe=False)

@csrf_exempt
@api_view(['PUT'])
def bulk_update_components(request):
    """
    API cập nhật nhiều Component trong một request.
    """
      # Lấy danh sách các Component từ body
    
    # if not isinstance(components_data, list):
    #     return JsonResponse({"error": "Dữ liệu phải là một danh sách"}, status=400)

    with transaction.atomic():
        components_data = request.data
        if not isinstance(components_data, list):
            return JsonResponse({"error": "Dữ liệu phải là một danh sách"}, status=400)
        print(type(components_data))
        for component_data in components_data:
            component_id = component_data.get("id")
            print(component_id, type(component_id), component_data.get("is_shorten"), type(component_data.get("is_shorten")) )
            if not isinstance(component_id, int):  # 🔥 Kiểm tra ID phải là số nguyên
                return JsonResponse({"error": "id phải là trường số nguyên"}, status= 400)

            
            if not component_id:
                return JsonResponse({"error": "Thiếu trường dữ liệu id"}, status= 400)

            try:
                item = component.objects.get(id=component_id)
            except Exception as e :
                print(e)
                return JsonResponse({"error": f'Component ID {component_id} không tồn tại'}, status= 400)
                
            serializer = componentSerializer(item, data=component_data, partial=True)
            
            try:                
                if serializer.is_valid():
                    
                    serializer.save()
                else:
                    return JsonResponse({"error": "Dữ liệu đầu vào không hợp lệ"}, status= 400)
            except Exception as e:
                print(e)
    return JsonResponse({"Success": "Lưu dữ liệu thành công"}, status=200)

@csrf_exempt
@api_view(['DELETE'])
def del_components(request, id):
    data = id
    try:
        lstcomponent = list(component.objects.get(id=data).descendants)
    except:
        return JsonResponse({"message": "id không tồn tại"}, status=400)

    lstdescendants = lstcomponent
    # print(lstdescendants, lstcomponent)
    try:
        for item in lstdescendants:
            component.objects.get(id = item).delete()
            for obj in component.objects.all():
                modified = False
                if isinstance(obj.descendants, dict):  # Chỉ xử lý nếu là dict
                        if item in list(obj.descendants):
                            del obj.data[item]
                            modified = True
                if modified:
                    obj.save()
    except Exception as e:
        print(e)
        return JsonResponse({"message": "Có lỗi xảy ra"}, status=400)
    return JsonResponse({"message": "Thành công"}, status=200)


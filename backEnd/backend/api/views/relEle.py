from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
from ..models.file import file
from ..models.concEle import Concele
from ..models.relEle import relEle
from ..models.gText import Gtext
from ..models.component import component
from rest_framework.response import Response
from rest_framework import status
from ..serializers.relEleSerializer import relEleSerializer
from ..permissions.permission import IsAdmin
from ..utils.Wraps import before_and_after_view



@permission_classes([IsAdmin])  
@api_view(['POST'])
@before_and_after_view(number=1)
def init_rel_conc(request, idLaw):
    try:
        fileitem = file.objects.get(id=idLaw)
        conceleitem = Concele.objects.filter(IdLaw = idLaw)
        releleitem = relEle.objects.filter(IdLaw = idLaw)
        gtext = Gtext.objects.filter(idLaw = idLaw)
        componentItem = component.objects.filter(idLaw=idLaw)
        if not componentItem.exists():
            return JsonResponse({'message': 'Component tương ứng chưa tồn tại'}, status=400)
        
        if not gtext.exists():
            return JsonResponse({'message': 'Không tồn tại gText tương ứng'}, status = 400)
    
        if not conceleitem.exists() and not releleitem.exists():
            with transaction.atomic():
                for item in gtext:
                    Flat = Concele.objects.filter(conC = item.ConcS).first()
                    if not item.ConcS.strip():
                        item.ConcS = '*'
                    concS1 = Concele.objects.create(
                            IdLaw = item.idLaw,
                            conC = item.ConcS,
                            Meaning = None,
                            descendants = item.descendants,
                            similar = None if not Flat else Flat.similar
                        )
                    Flat = Concele.objects.filter(conC = item.ConcO).first()
                    if not item.ConcO.strip():
                        item.ConcO = '*'
                    concO1 = Concele.objects.create(
                            IdLaw = item.idLaw,
                            conC = item.ConcO,
                            Meaning = None,
                            descendants = item.descendants,
                            similar = None if not Flat else Flat.similar
                        )
                    Flat = relEle.objects.filter(relation = item.ConcO).first()
                    if not item.Relation.strip():
                        continue
                    rel = relEle.objects.create(
                            IdLaw = item.idLaw,
                            relation = item.Relation,
                            Meaning = None,
                            descendants = item.descendants,
                            similar = None if not Flat else Flat.similar,
                            concS = concS1,
                            concO = concO1
                        )
    
    except file.DoesNotExist:
        return JsonResponse({'message': 'Không tồn tại file tương ứng'}, status = 400)
    except Exception as e:
        print(e)
        return JsonResponse({'message': 'Lỗi hệ thống'}, status = 400)

    return JsonResponse({'message': 'Khởi tạo thành công'}, status=200)


@permission_classes([IsAdmin])  
@api_view(['POST'])
def get_relele_list(request):
    data = request.data
    
    relele = relEle.objects.all()
    if data.get('idLaw'):
        relele = relele.filter(IdLaw_id = data.get('idLaw'))
    if data.get('Rel'):
        relele = relele.filter(relation__icontains = data.get('Rel'))
    if data.get('Meaning'):
        relele = relele.filter(Meaning__icontains = data.get('Meaning'))
    serializer = relEleSerializer(relele, many=True)
    return Response(serializer.data, status= status.HTTP_200_OK)



@permission_classes([IsAdmin])  
@api_view(['GET'])
def get_relele_detail(request, pk):
    try:
        relele = relEle.objects.get(pk=pk)
        serializer = relEleSerializer(relele)
        return Response(serializer.data)
    except relEle.DoesNotExist:
        return Response({'message': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


@permission_classes([IsAdmin])  
@api_view(['POST'])
def create_relele(request):
    serializer = relEleSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAdmin])  
@api_view(['PUT'])
def update_relele(request, id):
    try:
        relele = relEle.objects.get(id=id)
    except relEle.DoesNotExist:
        return Response({'message': 'Không tìm thấy'}, status=status.HTTP_400_BAD_REQUEST)
    data = request.data
    data['id']=id
    serializer = relEleSerializer(relele, data=data,partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAdmin])  
@api_view(['DELETE'])
def delete_relele(request, pk):
    try:
        relele = relEle.objects.get(pk=pk)
        relele.delete()
        return Response({'message': 'Deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except relEle.DoesNotExist:
        return Response({'message': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


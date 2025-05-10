# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models.concEle import Concele
from ..serializers.concEleSerializer import concEleSerializer
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from ..permissions.permission import IsSuperAdmin
from ..permissions.permission import IsAdmin
@permission_classes([IsAdmin])  
@api_view(['POST'])
def get_concele_list(request):
    data = request.data
    concele = Concele.objects.all()
    if data.get('idLaw'):
        concele = concele.filter(IdLaw_id = data.get('idLaw'))
    if data.get('Conc'):
        concele = concele.filter(conC__icontains = data.get('Conc'))
    if data.get('Meaning'):
        concele = concele.filter(Meaning__icontains = data.get('Meaning'))
    if not data.get('idLaw'):
        concele = Concele.objects.all()
        
    serializer = concEleSerializer(concele, many=True)
    return Response(serializer.data, status= status.HTTP_200_OK)


@permission_classes([IsAdmin])  
@api_view(['GET'])
def get_concele_detail(request, id):
    try:
        concele = Concele.objects.get(id=id)
        serializer = concEleSerializer(concele)
        return Response(serializer.data)
    except Concele.DoesNotExist:
        return Response({'message': 'Không tin thấy dữ liệu'}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAdmin])  
@api_view(['POST'])
def create_concele(request):
    serializer = concEleSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAdmin])  
@api_view(['PUT'])
def update_concele(request, id):
    try:
        concele = Concele.objects.get(id=id)
        data=request.data
        data['id']=id
        print(data)
    except Concele.DoesNotExist:
        return Response({'message': 'Không tìm thấy'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = concEleSerializer(concele, data=data,partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAdmin])  
@api_view(['DELETE'])
def delete_concele(request, pk):
    try:
        concele = Concele.objects.get(pk=pk)
        concele.delete()
        return Response({'message': 'Xóa thành công'}, status=status.HTTP_204_NO_CONTENT)
    except Concele.DoesNotExist:
        return Response({'message': 'Không tìm thấy'}, status=status.HTTP_400_BAD_REQUEST)

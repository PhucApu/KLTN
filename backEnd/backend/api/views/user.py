from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from ..models.user import User
from ..serializers.userSerializer import UserSerializer
from ..permissions.permission import IsSuperAdmin
from ..permissions.permission import IsAdmin
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken

# Thêm người dùng
@api_view(['POST'])
# @permission_classes([IsSuperAdmin])
@csrf_exempt
def user_create(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Sửa thông tin người dùng
@api_view(['PUT'])
@permission_classes([IsSuperAdmin])
def user_update(request):
    try: 
        user = User.objects.get(id=request.data.get("id"))
    except User.DoesNotExist:
        return Response({"detail": "Người dùng không tồn tại."}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = UserSerializer(user, data=request.data, partial=True) 
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Tìm kiếm người dùng theo ID
@api_view(['POST'])
@permission_classes([IsSuperAdmin])
def user_detail(request):
    try:
        user = User.objects.get(id= request.data.get('userid'))
    except User.DoesNotExist:
        return Response({"detail": "Người dùng không tồn tại."}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = UserSerializer(user)
    return Response(serializer.data)

# Tìm kiếm người dùng theo tên
@api_view(['POST'])
@permission_classes([IsAdmin])
def search_users(request):
    query = request.data.get('query', None)  # Lấy từ khóa tìm kiếm từ body của request
    
    if query is None:
        return Response(UserSerializer(User.objects.all(), many=True).data, status=status.HTTP_200_OK)
    
    # Tìm kiếm trên các trường không bảo mật: name, employee_code, address, cccd, ...
    users = User.objects.filter(
        username__icontains=query) | User.objects.filter(
        employee_code__icontains=query) | User.objects.filter(
        address__icontains=query) | User.objects.filter(
        cccd__icontains=query) | User.objects.filter(
        first_name__icontains=query) | User.objects.filter(
        last_name__icontains=query)
    
    # Nếu không tìm thấy người dùng nào
    if not users.exists():
        return Response({"detail": "Không tìm thấy người dùng nào với từ khóa này."}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])  
def me_detail(request):
    user = request.user  
    serializer = UserSerializer(user) 
    return Response(serializer.data)  

@api_view(['POST'])
@permission_classes([IsAuthenticated])  
def logout_view(request):
    refresh_token = request.data.get("refresh")
    if not refresh_token:
        return Response({"message": "Cần refresh token."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()  # đưa token vào danh sách cấm
        return Response({"message": "Logout thành công."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "Refresh token hết hạn hoặc không tồn tại."}, status=status.HTTP_400_BAD_REQUEST)
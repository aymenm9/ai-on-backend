from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from .serializers import UserSerializer
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
# Create your views here.

class CreateUser(APIView):
    """
    View to create a new user and return JWT tokens.
    """

    @extend_schema(
        request=UserSerializer,
        responses={
            201: UserSerializer,
        },
    )
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({'error': 'Username and password are required.'}, status=400)
        
        
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists.'}, status=400)
        
        user = User.objects.create_user(username=username, password=password)
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=201)


class MeView(generics.RetrieveAPIView):
    """
    Get current authenticated user's profile with all financial data.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get current user profile",
        description="Returns the authenticated user's profile including all financial data and AI preferences.",
        responses={
            200: UserSerializer,
        },
        tags=["Users"]
    )
    def get(self, request):
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
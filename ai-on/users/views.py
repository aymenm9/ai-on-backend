from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from .serializers import UserSerializer
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
# Create your views here.

class CreateUser(APIView):
    """
    View to create a new user and return JWT tokens.
    """
    @extend_schema(
        request={
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "password": {"type": "string"},
            },
            "required": ["username", "password"],
        },
        responses={
            201: {
                "type": "object",
                "properties": {
                    "refresh": {"type": "string"},
                    "access": {"type": "string"},
                },
            },
            400: {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                },
            },
        },
    )
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({'error': 'Username and password are required.'}, status=400)
        
        from django.contrib.auth.models import User
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists.'}, status=400)
        
        user = User.objects.create_user(username=username, password=password)
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=201)


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user
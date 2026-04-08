from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth import get_user_model
from django.shortcuts import render

from .serializers import (
    RegisterSerializer,
    ProfileSerializer,
    UserMeSerializer,
    ChangePasswordSerializer,
)
from django.http import HttpResponse

def home(request):
    return render(request, 'register.html')

User = get_user_model()

def profile_page(request):
    return render(request, 'profile.html')
def login_page(request):
    return render(request, 'register.html')

# ✅ Register
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {'message': 'Compte créé avec succès !', 'user_id': user.id},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ Profile (GET = read, POST = update)
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profil mis à jour !'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ Delete account (Django version replacing suppression_compte.php)
class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        password = request.data.get('password')

        if not user.check_password(password):
            return Response(
                {'error': 'Mot de passe incorrect.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.delete()
        return Response({'message': 'Compte supprimé définitivement.'})


# ✅ Change password
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response({'message': 'Mot de passe modifié avec succès.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ Template views
def register_page(request):
    return render(request, 'register.html')

def profile_page(request):
    return render(request, 'profile.html')
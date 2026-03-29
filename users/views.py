from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import render
from .serializers import (
    RegisterSerializer,
    ProfileSerializer,
    UserMeSerializer,
    ChangePasswordSerializer,
)


class RegisterView(APIView):
    """Public endpoint — creates a new user account."""
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


class ProfileView(APIView):
    """
    GET  — returns the logged-in user's full profile.
    POST — updates the logged-in user's profile (supports multipart for photo upload).
    Only the authenticated user can access their own profile.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profil mis à jour !'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """Allows an authenticated user to change their own password."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response(
                {'message': 'Mot de passe modifié avec succès.'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Template views ────────────────────────────────────────────────────────────

def register_page(request):
    return render(request, 'register.html')


def profile_page(request):
    return render(request, 'profile.html')

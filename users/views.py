from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .authentication import CookieJWTAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
User = get_user_model()


class RegisterView(APIView):
    permission_classes = []
    
    def post(self, request):
        try:
            data = request.data
            
            if not data.get('email') or not data.get('password') or not data.get('username'):
                return Response({
                    'status': 'error',
                    'message': 'Email, username et mot de passe requis'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if User.objects.filter(email=data['email']).exists():
                return Response({
                    'status': 'error',
                    'message': 'Cet email est déjà utilisé'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if User.objects.filter(username=data['username']).exists():
                return Response({
                    'status': 'error',
                    'message': 'Ce nom d\'utilisateur est déjà pris'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                phone=data.get('phone', ''),
                role=data.get('role', 'etudiant')
            )
            
            return Response({
                'status': 'success',
                'message': 'Utilisateur créé avec succès',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Erreur lors de la création du compte'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user = request.user
            photo_url = None
            if user.profile_photo:
                photo_url = request.build_absolute_uri(user.profile_photo.url)
            
            return Response({
                'status': 'success',
                'data': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': getattr(user, 'first_name', ''),
                    'last_name': getattr(user, 'last_name', ''),
                    'phone': getattr(user, 'phone', ''),
                    'date_of_birth': str(getattr(user, 'date_of_birth', '')) if getattr(user, 'date_of_birth', None) else '',
                    'role': getattr(user, 'role', 'etudiant'),
                    'purpose': getattr(user, 'purpose', ''),
                    'bio': getattr(user, 'bio', ''),
                    'profile_photo': photo_url,
                }
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Erreur lors du chargement du profil'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        try:
            user = request.user
            data = request.data
            
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'phone' in data:
                user.phone = data['phone']
            if 'date_of_birth' in data:
                user.date_of_birth = data['date_of_birth'] or None
            if 'role' in data:
                user.role = data['role']
            if 'purpose' in data:
                user.purpose = data['purpose']
            if 'bio' in data:
                user.bio = data['bio']
            
            user.save()
            
            photo_url = None
            if user.profile_photo:
                photo_url = request.build_absolute_uri(user.profile_photo.url)
            
            return Response({
                'status': 'success',
                'message': 'Profil mis à jour',
                'data': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                    'profile_photo': photo_url,
                }
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Erreur lors de la mise à jour du profil'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChangePasswordView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            user = request.user
            data = request.data
            
            old_password = data.get('old_password')
            new_password = data.get('new_password')
            
            if not old_password or not new_password:
                return Response({
                    'status': 'error',
                    'message': 'Ancien et nouveau mot de passe requis'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not user.check_password(old_password):
                return Response({
                    'status': 'error',
                    'message': 'Ancien mot de passe incorrect'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(new_password)
            user.save()
            
            return Response({
                'status': 'success',
                'message': 'Mot de passe modifié avec succès'
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Erreur lors du changement de mot de passe'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ProfilePhotoUploadView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        try:
            user = request.user
            photo = request.FILES.get('profile_photo')
            
            if not photo:
                return Response({
                    'status': 'error',
                    'message': 'Aucune photo fournie'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.profile_photo = photo
            user.save()
            
            photo_url = request.build_absolute_uri(user.profile_photo.url)
            
            return Response({
                'status': 'success',
                'message': 'Photo mise à jour',
                'profile_photo': photo_url
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Erreur lors du téléchargement de la photo'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CoverPhotoUploadView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        try:
            user = request.user
            photo = request.FILES.get('cover_photo')
            
            if not photo:
                return Response({
                    'status': 'error',
                    'message': 'Aucune photo fournie'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.cover_photo = photo
            user.save()
            
            photo_url = request.build_absolute_uri(user.cover_photo.url)
            
            return Response({
                'status': 'success',
                'message': 'Cover photo mise à jour',
                'cover_photo': photo_url
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Erreur lors du téléchargement de la cover photo'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
def register_login_page(request):
    return render(request, 'register.html')


from django.shortcuts import render, redirect
from .authentication import CookieJWTAuthentication

def profile_page(request):
    auth = CookieJWTAuthentication()
    try:
        user_auth_tuple = auth.authenticate(request)
        if user_auth_tuple:
            user, token = user_auth_tuple
        else:
            # No valid authentication, redirect to login
            return redirect('/api/users/')
    except Exception:
        # Authentication failed, redirect to login
        return redirect('/api/users/')
    
    return render(request, 'profile.html', {'user': user})

def profile_info_page(request):
    return render(request, 'profile_info.html')
from django.shortcuts import redirect
from django.urls import resolve

class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        exempt_urls = [
            'profile_info',
            'profile',
            'logout',
            'login',
            'register',
            'register-login',
            'token-refresh',
        ]
        
        try:
            current_url = resolve(request.path_info).url_name
        except:
            current_url = None
        
        if current_url in exempt_urls:
            return self.get_response(request)
        
        if request.path.startswith('/api/'):
            return self.get_response(request)
        
        profile_complete = (
            request.user.first_name and 
            request.user.last_name and 
            request.user.role
        )
        
        if not profile_complete and current_url != 'profile_info':
                return redirect('profile_info')
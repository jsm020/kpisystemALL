# your_app/middleware.py

from django.shortcuts import redirect

class AdminRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the user is trying to access /admin/login/?next=/admin/
        if request.path == '/admin/login/' and request.GET.get('next') == '/admin/':
            return redirect('/admin/login/?next=/')
        
        # Process the request
        response = self.get_response(request)
        return response

from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages


class RoleBasedAccessMiddleware:
    """Middleware to enforce role-based access control"""
    
    # Define which roles can access which URL patterns
    ROLE_URL_MAP = {
        'tutor': ['/tutors/', '/bookings/', '/payments/', '/messages/', '/reviews/'],
        'student': ['/students/', '/bookings/', '/payments/', '/messages/', '/reviews/'],
        'parent': ['/students/', '/bookings/', '/payments/', '/messages/', '/reviews/'],
        'city_admin': ['/admin/city/', '/admin/'],
        'global_admin': ['/admin/global/', '/admin/city/', '/admin/'],
    }
    
    # URLs that don't require role checking
    PUBLIC_URLS = [
        '/',
        '/users/login/',
        '/users/register/',
        '/users/logout/',
        '/tutors/search/',
        '/tutors/become-tutor/',
        '/tutors/',  # Allow public tutor detail pages
        '/static/',
        '/media/',
        '/api/',
        '/cms/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip middleware for unauthenticated users (handled by login_required)
        if not request.user.is_authenticated:
            response = self.get_response(request)
            return response
        
        # Check if URL requires role-based access
        path = request.path
        
        # Skip public URLs
        if any(path.startswith(url) for url in self.PUBLIC_URLS):
            response = self.get_response(request)
            return response
        
        # Check role-based access
        user_role = request.user.role
        allowed_urls = self.ROLE_URL_MAP.get(user_role, [])
        
        # FIRST: Allow access to admin panel for admins (check this BEFORE other checks)
        if user_role in ['city_admin', 'global_admin'] and path.startswith('/admin/'):
            response = self.get_response(request)
            return response
        
        # Allow access to profile and settings (for all authenticated users)
        if path.startswith('/users/profile/') or path.startswith('/users/settings/'):
            response = self.get_response(request)
            return response
        
        # Allow public tutor detail pages (viewing tutor profiles)
        if path.startswith('/tutors/') and path.count('/') == 2:  # /tutors/<id>/
            response = self.get_response(request)
            return response
        
        # Check if user is trying to access a URL not allowed for their role
        if not any(path.startswith(url) for url in allowed_urls):
            # Redirect unauthorized users to their appropriate dashboard
            messages.error(request, 'You do not have permission to access this page.')
            from django.urls import reverse
            try:
                if user_role == 'tutor':
                    return redirect(reverse('tutors:dashboard'))
                elif user_role in ['student', 'parent']:
                    return redirect(reverse('students:dashboard'))
                elif user_role == 'city_admin':
                    return redirect(reverse('admin_panel:city_dashboard'))
                elif user_role == 'global_admin':
                    return redirect(reverse('admin_panel:global_dashboard'))
            except:
                pass
            return redirect('/')
        
        response = self.get_response(request)
        return response


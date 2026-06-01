"""
URL configuration for VerifiHireAI_backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from api import views

urlpatterns = [
    path('', views.api_root, name='api-root'),
    path('django-admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/ai/', include('ai_assessments.urls')),
    path('api/ai-candidates/', include('ai_candidates.urls')),
]

# Serve media files in development (or locally when DEBUG=False)
from django.urls import re_path
from django.views.static import serve

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]


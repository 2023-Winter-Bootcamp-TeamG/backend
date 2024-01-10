from django.urls import path, re_path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.contrib import admin
from django.urls import path, include
from photo.views import PhotoUploadView

schema_view = get_schema_view(
    openapi.Info(
        title = "API Documentation",
        default_version='v1',
        description="API documentation for myproject",
    ),
    public = True,
    permission_classes=(permissions.AllowAny,),
    url = 'http://127.0.0.1:8000/',
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('member.urls')),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', include('photo.urls')),
]
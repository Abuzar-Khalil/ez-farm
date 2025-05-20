"""
URL configuration for ez_farming project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Custom views for homepage or simple responses
from ezcore.views import home_view
from user.views import user_view
from ezdairy.views import dairy_view
from ezmeat.views import meat_view
from ezanimal.views import animal_view
from ezcore.health_and_feed.views import haf_view
from ezcore.inventory_and_sales.views import ias_view

# Swagger/OpenAPI schema setup
schema_view = get_schema_view(
   openapi.Info(
      title="EZ Farming API",
      default_version='v1',
      description="API for EZ Farming Livestock Management System",
      terms_of_service="https://www.ezfarming.com/terms/",
      contact=openapi.Contact(email="contact@ezfarming.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),

    # Main API endpoints
    path('api/', include('ez_farming.api_urls')),

    # Frontend-compatible views (basic/custom views)
    path('', home_view, name='home'),

    # API documentation (Swagger and Redoc)
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

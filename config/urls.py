from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.urls import path

def trigger_error(request):
    division_by_zero = 1 / 0


schema_view = get_schema_view(
   openapi.Info(
      title="Coursefy API",
      default_version='v1',
      description="API for project Coursify",
      terms_of_service="https://tts.uz/",
      contact=openapi.Contact(email="contact@tts.uz")
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('sentry-debug/', trigger_error),
    # path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('api/v1/course/', include('course.urls')),
    path('api/v1/test/', include('tests.urls')),
    path('api/v1/rating/', include('rating.urls')),
    path('api/v1/accounts/', include('accounts.urls')),
    # path('api/v1/payment/', include('payment.urls')),
    path('payment/', include('payment.urls')),
    path('payme/', include("my_payme.urls")),
    path('api/v1/chat/', include('chat.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path('pages/', include('django.contrib.flatpages.urls')),
)

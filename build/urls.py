from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),  # accounts app handles landing, login, signup
    # other apps
    path('skills/', include('skills.urls')),
    path('ai_chat/', include('ai_chat.urls')),
    path('assessment/', include('assessment.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

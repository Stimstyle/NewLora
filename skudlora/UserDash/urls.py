from django.urls import path
from UserDash.views import index
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('index/', index, name='index'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
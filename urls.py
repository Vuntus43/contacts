from django.contrib import admin
from django.urls import path, include
from django.conf import settings                # ← добавь
from django.conf.urls.static import static      # ← добавь

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('map.urls')),
]


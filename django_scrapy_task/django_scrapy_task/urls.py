from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    url(r'^api/', include('api.urls', namespace='api')),
    path('admin/', admin.site.urls),
]

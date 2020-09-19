from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view
from api import views

app_name = 'api'
router = DefaultRouter()
# router.register('user_notes', views.UserPrivateNotesView, base_name='user_private_notes')

# rest framework schema
rest_schema_view = get_schema_view(title="PIGS INFO API")

urlpatterns = [
    url(r'', include(router.urls)),
    url(r'schema/$', rest_schema_view)
]

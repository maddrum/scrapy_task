from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view
from api import views

app_name = 'api'
router = DefaultRouter()
router.register('list', views.ListDataView, basename='list_all_data')
router.register('mp', views.ListDataView, basename='list_single_data')
router.register('search', views.SearchNameView, basename='search_name')
# rest framework schema
rest_schema_view = get_schema_view(title="PIGS CATALOGUE API")

urlpatterns = [
    url(r'', include(router.urls)),
    url(r'schema/$', rest_schema_view)
]

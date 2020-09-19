import datetime

from api.serializers import BaseDataSerializer
from crawler_app.models import ScrapedData
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class ResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 240


class LoginUser(viewsets.ViewSet):
    """Shows user token"""
    serializer_class = AuthTokenSerializer

    def create(self, request, *args, **kwargs):
        return ObtainAuthToken().post(request)


class ListDataView(viewsets.ModelViewSet):
    """
    Provides summarized list data for all records or for single record
    """
    serializer_class = BaseDataSerializer
    http_method_names = ['get', ]
    queryset = ScrapedData.objects.all()
    pagination_class = ResultsSetPagination

    def get_queryset(self):
        qs = super().get_queryset()
        if 'pp' in self.request.query_params:
            criteria = self.request.query_params.get('pp')
            qs = qs.filter(political_party=criteria)
        if 'dob' in self.request.query_params:
            criteria_str = self.request.query_params.get('dob')
            criteria_date = datetime.datetime.strptime(criteria_str, '%Y%m%d').date()
            print(criteria_date)
            qs = qs.filter(date_of_birth=criteria_date)
        return qs


class LoggedOnlyListDataView(ListDataView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class SearchNameView(viewsets.ViewSet):
    """Search by name"""

    def create(self, request):
        if 'name' not in request.POST:
            return Response('ERROR: You must have a name parameter', status=422)
        criteria = str(self.request.POST.get('name')).upper()
        if len(criteria) == 0:
            return Response('ERROR: No value for name', status=422)
        qs = ScrapedData.objects.filter(name__contains=criteria)
        if not qs.exists():
            return Response('No results found', status=200)
        serializer = BaseDataSerializer(qs, many=True)
        return Response(serializer.data)

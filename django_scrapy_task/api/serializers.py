from crawler_app.models import ScrapedData
from rest_framework import serializers


class BaseDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapedData
        fields = (
            'id', 'name', 'avatar', 'country_of_birth', 'place_of_birth', 'date_of_birth', 'job', 'languages',
            'political_party', 'email')


class NameSearchSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)

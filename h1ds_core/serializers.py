from rest_framework import serializers
from h1ds_core.models import Node, Filter

class NodeSerializer(serializers.Serializer):
    shot = serializers.Field()
    path = serializers.CharField()
    
    

class FilterSerializer(serializers.Serializer):
    pass




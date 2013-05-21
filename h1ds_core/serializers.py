import numpy as np

from rest_framework import serializers
from h1ds_core.models import Node, Filter

class NodeSerializer(serializers.ModelSerializer):
    # parent
    # children
    # slug ?
    # data (optional depending on ?show_data query string
    path = serializers.CharField()
    parent = serializers.HyperlinkedRelatedField(view_name='node-detail', lookup_field='nodepath')
    children = serializers.HyperlinkedRelatedField(view_name='node-detail', lookup_field='nodepath', many=True)
    data = serializers.Field()
    class Meta:
        model = Node
        fields = ('path', 'parent', 'children', 'data')

    #data = serializers.SerializerMethodField('get_node_data')

    def get_node_data(self, obj):
        d = obj.read_primary_data()
        if np.isscalar(d) or d == None:
            return d
        else:
            return d.tolist()
    
    """
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    slug = models.SlugField()
    has_data = models.BooleanField(default=True)
    dimension = models.PositiveSmallIntegerField(blank=True, null=True)
    dtype = models.CharField(max_length=16)
    """
    

class FilterSerializer(serializers.Serializer):
    pass




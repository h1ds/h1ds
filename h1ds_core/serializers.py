import numpy as np

from rest_framework import serializers
from h1ds_core.models import Node, Filter, Shot

#class NodeSerializer(serializers.ModelSerializer):
class NodeSerializer(serializers.HyperlinkedModelSerializer):
    # parent
    # children
    # slug ?
    # data (optional depending on ?show_data query string
    path = serializers.CharField()
    parent = serializers.HyperlinkedRelatedField(view_name='node-detail', lookup_field='nodepath')
    children = serializers.HyperlinkedRelatedField(view_name='node-detail', lookup_field='nodepath', many=True)
    data = serializers.Field()
    url = serializers.HyperlinkedIdentityField(view_name="node-detail", slug_field="nodepath")
    class Meta:
        model = Node
        fields = ('path', 'parent', 'children', 'data', 'url')

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



class ShotSerializer(serializers.HyperlinkedModelSerializer):
    number = serializers.IntegerField()
    timestamp = serializers.DateTimeField()
    root_nodes = serializers.SerializerMethodField('get_root_nodes')

    class Meta:
        model = Shot
        fields = ('number', 'timestamp', 'root_nodes', )

    def get_root_nodes(self, obj):
        return [{'path':n.path, 'url':n.get_absolute_url()}  for n in obj.root_nodes]

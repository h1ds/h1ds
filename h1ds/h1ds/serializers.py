import hashlib
import numpy as np

from rest_framework import serializers
from rest_framework.reverse import reverse
from h1ds_core.models import Node, Filter, Shot
from django.core.urlresolvers import NoReverseMatch

import warnings

class NodeHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    """Small hack to allow multiple kwargs on reverse lookup."""
    def field_to_native(self, obj, field_name):
        request = self.context.get('request', None)
        format = self.context.get('format', None)
        view_name = self.view_name or self.parent.opts.view_name
        # This line is the only difference between NodeHyperlinkedIdentityField and HyperlinkedIdentityField
        kwargs = {'shot':obj.shot.number, 'nodepath':obj.nodepath}

        if request is None:
            warnings.warn("Using `HyperlinkedIdentityField` without including the "
                          "request in the serializer context is deprecated. "
                          "Add `context={'request': request}` when instantiating the serializer.",
                          DeprecationWarning, stacklevel=4)

        # By default use whatever format is given for the current context
        # unless the target is a different type to the source.
        #
        # Eg. Consider a HyperlinkedIdentityField pointing from a json
        # representation to an html property of that representation...
        #
        # '/snippets/1/' should link to '/snippets/1/highlight/'
        # ...but...
        # '/snippets/1/.json' should link to '/snippets/1/highlight/.html'
        if format and self.format and self.format != format:
            format = self.format

        try:
            return reverse(view_name, kwargs=kwargs, request=request, format=format)
        except NoReverseMatch:
            pass

        slug = getattr(obj, self.slug_field, None)

        if not slug:
            raise Exception('Could not resolve URL for field using view name "%s"' % view_name)

        kwargs = {self.slug_url_kwarg: slug}
        try:
            return reverse(view_name, kwargs=kwargs, request=request, format=format)
        except NoReverseMatch:
            pass

        kwargs = {self.pk_url_kwarg: obj.pk, self.slug_url_kwarg: slug}
        try:
            return reverse(view_name, kwargs=kwargs, request=request, format=format)
        except NoReverseMatch:
            pass

        raise Exception('Could not resolve URL for field using view name "%s"' % view_name)


class NodeHyperlinkedField(serializers.HyperlinkedRelatedField):
    def get_url(self, obj, view_name, request, format):
        kwargs = {'shot': obj.shot.number, 'nodepath': obj.nodepath}#, 'format':format}
        return reverse(view_name, kwargs=kwargs, request=request, format=format)


    def get_object(self, queryset, view_name, view_args, view_kwargs):
        shot = view_kwargs['shot']
        nodepath = view_kwargs['nodepath']
        checksum = hashlib.sha1(nodepath).hexdigest()
        node = Node.objects.get(shot__number=shot, path_checksum=checksum)
        return node

class DataField(serializers.WritableField):
    def to_native(self, obj):
        if np.isscalar(obj):
            return obj
        else:
            output = [d.tolist() for d in obj]
            return output
        
    def from_native(self,obj):
        pass

class DataSerializer(serializers.Serializer):
    """Serializer for a single data object.

    value
    dim
    name
    value_units
    dim_units
    dtype
    meta
    """
    
    name = serializers.CharField()
    value = DataField()
    dimension = DataField()
    value_units = serializers.CharField()
    dimension_units = serializers.CharField()
    value_dtype = serializers.CharField()
    dimension_dtype = serializers.CharField()
    metadata = serializers.WritableField()

    
class NodeSerializer(serializers.HyperlinkedModelSerializer):
    # slug ?
    # data (optional depending on ?show_data query string
    path = serializers.CharField()
    parent = NodeHyperlinkedField(view_name='node-detail')
    children = NodeHyperlinkedField(view_name='node-detail', many=True)
    #data = serializers.Field()
    data = DataSerializer(source='get_data')
    url = NodeHyperlinkedIdentityField(view_name="node-detail", slug_field="nodepath")
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

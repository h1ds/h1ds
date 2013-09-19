import hashlib
import numpy as np

from rest_framework import serializers
from rest_framework.reverse import reverse
from h1ds.models import Node, Shot, Device
from django.core.urlresolvers import NoReverseMatch
from types import NoneType

import warnings

class NodeHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    """Small hack to allow multiple kwargs on reverse lookup."""
    def field_to_native(self, obj, field_name):
        request = self.context.get('request', None)
        format = self.context.get('format', None)
        view_name = self.view_name or self.parent.opts.view_name
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

        # Return the hyperlink, or error if incorrectly configured.
        try:
            return self.get_url(obj, view_name, request, format, kwargs)
        except NoReverseMatch:
            msg = (
                'Could not resolve URL for hyperlinked relationship using '
                'view name "%s". You may have failed to include the related '
                'model in your API, or incorrectly configured the '
                '`lookup_field` attribute on this field.'
            )
            raise Exception(msg % view_name)

    def get_url(self, obj, view_name, request, format, custom_kwargs):
        """
        Given an object, return the URL that hyperlinks to the object.

        May raise a `NoReverseMatch` if the `view_name` and `lookup_field`
        attributes are not configured to correctly match the URL conf.

        
        """
        lookup_field = getattr(obj, self.lookup_field)
        # kwargs = {self.lookup_field: lookup_field}
        kwargs = custom_kwargs
        try:
            return reverse(view_name, kwargs=kwargs, request=request, format=format)
        except NoReverseMatch:
            pass

        if self.pk_url_kwarg != 'pk':
            # Only try pk if it has been explicitly set.
            # Otherwise, the default `lookup_field = 'pk'` has us covered.
            pk = obj.pk
            kwargs = {self.pk_url_kwarg: pk}
            try:
                return reverse(view_name, kwargs=kwargs, request=request, format=format)
            except NoReverseMatch:
                pass

        slug = getattr(obj, self.slug_field, None)
        if slug is not None:
            # Only try slug if it corresponds to an attribute on the object.
            kwargs = {self.slug_url_kwarg: slug}
            try:
                ret = reverse(view_name, kwargs=kwargs, request=request, format=format)
                if self.slug_field == 'slug' and self.slug_url_kwarg == 'slug':
                    # If the lookup succeeds using the default slug params,
                    # then `slug_field` is being used implicitly, and we
                    # we need to warn about the pending deprecation.
                    msg = 'Implicit slug field hyperlinked fields are pending deprecation.' \
                          'You should set `lookup_field=slug` on the HyperlinkedRelatedField.'
                    warnings.warn(msg, PendingDeprecationWarning, stacklevel=2)
                return ret
            except NoReverseMatch:
                pass

        raise NoReverseMatch()


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
        if np.isscalar(obj) or type(obj) == NoneType:
            return obj
        else:
            output = []
            for d in obj: # TODO: hack
                if np.isscalar(d) or type(d) == NoneType:
                    output.append(d)
                else:
                    output.append(d.tolist())
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


class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField()
    description = serializers.CharField()
    slug = serializers.SlugField()

    class Meta:
        model = Device
        fields = ('name', 'description', 'slug')

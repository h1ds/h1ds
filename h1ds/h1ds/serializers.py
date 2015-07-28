import hashlib
import numpy as np

from rest_framework import serializers
from rest_framework.reverse import reverse
from h1ds.models import SubTree, Shot, Device, Node, Tree
from django.core.urlresolvers import NoReverseMatch
from types import NoneType

import warnings


class NodeHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    """Small hack to allow multiple kwargs on reverse lookup."""

    def field_to_native(self, obj, field_name):
        request = self.context.get('request', None)
        format = self.context.get('format', None)
        view_name = self.view_name or self.parent.opts.view_name
        kwargs = {'device': obj.get_device().slug,
                  'shot': obj.get_shot_number(),
                  'tree': obj.get_tree(),
                  'nodepath': obj.get_nodepath()
                  }

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
        kwargs = {'device': obj.shot.device.slug, 'shot': obj.shot.number,
                  'nodepath': obj.nodepath}  # , 'format':format}
        return reverse(view_name, kwargs=kwargs, request=request, format=format)

    def get_object(self, queryset, view_name, view_args, view_kwargs):
        shot = view_kwargs['shot']
        nodepath = view_kwargs['nodepath']
        checksum = hashlib.sha1(nodepath).hexdigest()
        subtree = SubTree.objects.get(shot__number=shot, path_checksum=checksum)
        return subtree


class DataField(serializers.WritableField):
    def to_native(self, obj):
        if np.isscalar(obj) or type(obj) == NoneType:
            return obj
        else:
            output = []
            for d in obj:  # TODO: hack
                if np.isscalar(d) or type(d) == NoneType:
                    output.append(d)
                else:
                    output.append(d.tolist())
            return output

    def from_native(self, obj):
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
    value_labels = serializers.WritableField()
    dimension_labels = serializers.WritableField()


class SubTreeSerializer(serializers.HyperlinkedModelSerializer):
    # slug ?
    # data (optional depending on ?show_data query string
    path = serializers.CharField()
    parent = NodeHyperlinkedField(view_name='node-detail')
    children = NodeHyperlinkedField(view_name='node-detail', many=True)
    #data = serializers.Field()
    data = DataSerializer(source='get_data')
    url = NodeHyperlinkedIdentityField(view_name="node-detail", slug_field="nodepath")

    class Meta:
        model = SubTree
        fields = ('path', 'parent', 'children', 'data', 'url')


class NodeSerializer(serializers.HyperlinkedModelSerializer):
    url = NodeHyperlinkedIdentityField(view_name="node-detail", slug_field="nodepath")
    data = DataSerializer(source='get_data')

    class Meta:
        model = Node
        fields = ('url', 'data')


class PathMapSerializer(serializers.Serializer):
    """Serializer for a PathMap instance.

    """
    pass


class FilterSerializer(serializers.Serializer):
    pass


class ShotSerializer(serializers.HyperlinkedModelSerializer):
    number = serializers.IntegerField()
    timestamp = serializers.DateTimeField()
    #root_pathmaps = serializers.SerializerMethodField('get_root_pathmaps')

    class Meta:
        model = Shot
        fields = ('number', 'timestamp', 'device')

    #def get_root_pathmaps(self, obj):
    #    return [{'path': pm.node_path.get_node_name(), 'url': pm.get_absolute_url()} for pm in obj.root_pathmaps]


class TreeSerializer(serializers.HyperlinkedModelSerializer):
    """Serialise a tree instance.

    TODO - include root nodes, shot etc...

    If a shot instance is passed as extra context, then the root nodes for that shot will be included.

    """

    name = serializers.CharField()
    data_backend = serializers.CharField()
    #shot = ShotSerializer()
    #root_nodes = NodeSerializer(many=True)

    class Meta:
        model = Tree
        fields = ('name', 'data_backend', )

class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField()
    description = serializers.CharField()
    slug = serializers.SlugField()
    latest_shot = ShotSerializer()

    class Meta:
        model = Device
        fields = ('name', 'description', 'slug', 'latest_shot')

# Set the device field here, after DeviceSerializer has been defined.
ShotSerializer.base_fields['device'] = DeviceSerializer()

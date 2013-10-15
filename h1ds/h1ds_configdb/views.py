from django.http import Http404
from django.views.generic.edit import FormView
from django import forms
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponseRedirect

from h1ds_configdb.models import ConfigDBFileType, ConfigDBFile, ConfigDBPropertyType

DEFAULT_RESULTS_PER_PAGE = 10


class ConfigDBSelectionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        """Form for user to filter results.
        """
        super(ConfigDBSelectionForm, self).__init__(*args, **kwargs)

        # Add checkboxes for each file type
        for configdb_filetype in ConfigDBFileType.objects.all():
            self.fields['filetype_%s' % configdb_filetype.slug] = forms.BooleanField(required=False,
                                                                                     label=configdb_filetype.name)

        # Add min/max for numeric properties.
        for prop in ConfigDBPropertyType.objects.all():
            # Float
            if prop.value_type == 'Float':
                self.fields['property_min_%s' % prop.slug] = forms.FloatField(required=False,
                                                                              label="%s (min)" % prop.name)
                self.fields['property_max_%s' % prop.slug] = forms.FloatField(required=False,
                                                                              label="%s (max)" % prop.name)
            # Integer
            elif prop.value_type == 'Integer':
                self.fields['property_min_%s' % prop.slug] = forms.IntegerField(required=False,
                                                                                label="%s (min)" % prop.name)
                self.fields['property_max_%s' % prop.slug] = forms.IntegerField(required=False,
                                                                                label="%s (max)" % prop.name)

        # Let the user specify number of results per page.
        self.fields['results_per_page'] = forms.IntegerField(required=False, label="Number of results per page.")


class HomeView(FormView):
    template_name = 'h1ds_configdb/configdb_home.html'

    form_class = ConfigDBSelectionForm

    def get_initial_filetypes(self):
        initial_filetypes = {}
        all_filetypes = [i.slug for i in ConfigDBFileType.objects.all()]
        if self.kwargs["filetype_str"] in ["all", "all_filetypes"]:
            for ft in all_filetypes:
                initial_filetypes['filetype_%s' % ft] = True
            return initial_filetypes
        requested_filetypes = self.kwargs["filetype_str"].split("+")
        for filetype in requested_filetypes:
            if filetype in all_filetypes:
                initial_filetypes['filetype_%s' % filetype] = True
        if not initial_filetypes:
            raise Http404

        return initial_filetypes

    def get_initial_filters(self):
        initial_filters = {}
        try:
            requested_filters = self.kwargs["filter_str"].split("+")
        except KeyError:
            return initial_filters

        for rf in requested_filters:
            split_rf = rf.split("__")
            if split_rf[1] == 'bw':
                initial_filters['property_min_%s' % split_rf[0]] = split_rf[2]
                initial_filters['property_max_%s' % split_rf[0]] = split_rf[3]
            elif split_rf[1] == 'lt':
                initial_filters['property_max_%s' % split_rf[0]] = split_rf[2]
            elif split_rf[1] == 'gt':
                initial_filters['property_min_%s' % split_rf[0]] = split_rf[2]
        return initial_filters


    def get_initial(self):
        initial = {}
        initial.update(self.get_initial_filetypes())
        initial.update(self.get_initial_filters())
        initial['results_per_page'] = self.request.GET.get('results_per_page', DEFAULT_RESULTS_PER_PAGE)
        return initial

    def get_filter_str(self, properties):
        filter_strings = []
        for k, v in properties.items():
            if v.has_key('min') and v.has_key('max'):
                filter_strings.append("%s__bw__%s__%s" % (k, str(v['min']), str(v['max'])))
            elif v.has_key('min'):
                filter_strings.append("%s__gt__%s" % (k, str(v['min'])))
            elif v.has_key('max'):
                filter_strings.append("%s__lt__%s" % (k, str(v['max'])))
        return "+".join(filter_strings)

    def form_valid(self, form):
        filetypes = []
        properties = {}
        for k, v in form.cleaned_data.items():
            if k.startswith("filetype_") and v == True:
                filetypes.append(k[9:])
            elif k.startswith("property_") and v is not None:
                property_name = k[13:]
                filter_type = k[9:12]
                if not properties.has_key(property_name):
                    properties[property_name] = {}
                properties[property_name][filter_type] = v

        filetype_str = "+".join(filetypes)

        filter_str = self.get_filter_str(properties)

        if not filetype_str:
            filetype_str = "all_filetypes"

        kwargs = {'filetype_str': filetype_str}

        querystring = ""
        rpp = int(self.request.POST.get('results_per_page', DEFAULT_RESULTS_PER_PAGE))
        if rpp != DEFAULT_RESULTS_PER_PAGE:
            querystring = "?results_per_page=%d" % (rpp)

        if filter_str:
            kwargs['filter_str'] = filter_str
            return HttpResponseRedirect(reverse("h1ds-configdb-filtered", kwargs=kwargs) + querystring)
        else:
            return HttpResponseRedirect(reverse("h1ds-configdb-filetypes", kwargs=kwargs) + querystring)


    def get_context_data(self, **kwargs):
        # Get slugs for requested filetypes.
        filetype_slugs = [i[9:] for i in kwargs['form'].initial.keys() if i.startswith("filetype_")]

        # Get only results for these filetypes.
        all_files = ConfigDBFile.objects.filter(filetype__slug__in=filetype_slugs)

        # Now apply the property filters.
        for fk, fv in [i for i in kwargs['form'].initial.items() if i[0].startswith('property_')]:
            slug = fk[13:]
            value_type = ConfigDBPropertyType.objects.get(slug=slug).get_value_type_display()
            # For now we only support numeric types, with min/max filters.
            if value_type == 'Float':
                if fk[9:12] == 'min':
                    all_files = all_files.filter(configdbproperty__configdb_propertytype__slug=slug,
                                                 configdbproperty__value_float__gte=fv)
                elif fk[9:12] == 'max':
                    all_files = all_files.filter(configdbproperty__configdb_propertytype__slug=slug,
                                                 configdbproperty__value_float__lte=fv)
            elif value_type == 'Integer':
                if fk[9:12] == 'min':
                    all_files = all_files.filter(configdbproperty__configdb_propertytype__slug=slug,
                                                 configdbproperty__value_integer__gte=fv)
                elif fk[9:12] == 'max':
                    all_files = all_files.filter(configdbproperty__configdb_propertytype__slug=slug,
                                                 configdbproperty__value_integer__lte=fv)

        paginator = Paginator(all_files, int(self.request.GET.get('results_per_page', DEFAULT_RESULTS_PER_PAGE)))
        kwargs['n_files'] = len(all_files)

        try:
            page = int(self.request.GET.get('page', '1'))
        except ValueError:
            page = 1

        try:
            kwargs['config_files'] = paginator.page(page)
        except (EmptyPage, InvalidPage):
            kwargs['config_files'] = paginator.page(paginator.num_pages)

        return kwargs

from django.shortcuts import render_to_response
#from django.template import RequestContext
#from django.http import HttpResponseRedirect
from django.http import Http404
from django.views.generic.edit import FormView
from django import forms
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType

from h1ds_configdb.models import ConfigDBFileType, ConfigDBFile, ConfigDBPropertyType, ConfigDBStringProperty, ConfigDBFloatProperty, ConfigDBIntProperty


class ConfigDBSelectionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ConfigDBSelectionForm, self).__init__(*args, **kwargs)
        
        for configdb_filetype in ConfigDBFileType.objects.all():
            self.fields['filetype_%s' %configdb_filetype.slug] = forms.BooleanField(required=False, label=configdb_filetype.name)
        
        # numeric fields.
        for prop in ConfigDBPropertyType.objects.all():
            if prop.content_type.model_class() == ConfigDBFloatProperty:
                self.fields['property_min_%s' %prop.slug] = forms.FloatField(required=False, label="%s (min)" %prop.name)
                self.fields['property_max_%s' %prop.slug] = forms.FloatField(required=False, label="%s (max)" %prop.name)
            elif prop.content_type.model_class() == ConfigDBIntProperty:
                self.fields['property_min_%s' %prop.slug] = forms.IntegerField(required=False, label="%s (min)" %prop.name)
                self.fields['property_max_%s' %prop.slug] = forms.IntegerField(required=False, label="%s (max)" %prop.name)
                

class HomeView(FormView):
    template_name = 'h1ds_configdb/configdb_home.html'

    form_class = ConfigDBSelectionForm
    
    def get_initial_filetypes(self):
        initial_filetypes = {}
        all_filetypes = [i.slug for i in ConfigDBFileType.objects.all()]
        if self.kwargs["filetype_str"] in ["all", "all_filetypes"]:
            return all_filetypes
        requested_filetypes = self.kwargs["filetype_str"].split("+")

        for filetype in requested_filetypes:
            if filetype in all_filetypes:
                initial_filetypes['filetype_%s' %filetype] = True
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
                initial_filters['property_min_%s' %split_rf[0]] = split_rf[2]
                initial_filters['property_max_%s' %split_rf[0]] = split_rf[3]
            elif split_rf[1] == 'lt':
                initial_filters['property_max_%s' %split_rf[0]] = split_rf[2]
            elif split_rf[1] == 'gt':
                initial_filters['property_min_%s' %split_rf[0]] = split_rf[2]
        return initial_filters
        

    def get_initial(self):
        initial = {}
        initial.update(self.get_initial_filetypes())
        initial.update(self.get_initial_filters())
        return initial
        
    def get_filter_str(self, properties):
        filter_strings = []
        for k,v in properties.items():
            if v.has_key('min') and v.has_key('max'):
                filter_strings.append("%s__bw__%s__%s" %(k,str(v['min']), str(v['max'])))
            elif v.has_key('min'):
                filter_strings.append("%s__gt__%s" %(k,str(v['min'])))
            elif v.has_key('max'):
                filter_strings.append("%s__lt__%s" %(k,str(v['max'])))
        return "+".join(filter_strings)

    def form_valid(self, form):
        filetypes = []
        properties = {}
        for k,v in form.cleaned_data.items():
            if k.startswith("filetype_") and v==True:
                filetypes.append(k[9:])
            elif k.startswith("property_") and v != None:
                property_name = k[13:]
                filter_type = k[9:12]
                if not properties.has_key(property_name):
                    properties[property_name] = {}
                properties[property_name][filter_type] = v

        filetype_str = "+".join(filetypes)

        filter_str = self.get_filter_str(properties)

        if not filetype_str:
            filetype_str = "all_filetypes"

        if filter_str:
            return HttpResponseRedirect(reverse("h1ds-configdb-filtered", kwargs={'filetype_str':filetype_str, 'filter_str':filter_str}))
        else:
            return HttpResponseRedirect(reverse("h1ds-configdb-filetypes", kwargs={'filetype_str':filetype_str}))
    

    def get_context_data(self, **kwargs):
        filetype_slugs = [i[9:] for i in kwargs['form'].initial.keys() if i.startswith("filetype_")]
        all_files = ConfigDBFile.objects.filter(filetype__slug__in=filetype_slugs).all()
        paginator = Paginator(all_files, 50)
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

        


"""
def _configdb_home(request):
    config_list = []
    for khx in range(0,121):
        kh = khx*0.01
        config_list.append({'name':'kh:%.2f, kv:1.00' %kh, 
                            'url':'/configurations/kh%.2f/' %kh, 
                            'kh':"%.2f" %kh, 'kv':"1.00"})

    return render_to_response('h1ds_configdb/configdb_home.html', {'configs':config_list},
                              context_instance=RequestContext(request),
                              )

def kh_string_w_neg(kh):
    kh_str = "%1.3f" %kh
    if kh_str[0] != '-':
        kh_str = '0'+kh_str
    return kh_str

def config_overview(request, config_id):
    # only support config_id = khx.xx for now
    kh = config_id[2:]
    kh_val = "%.2f" %float(kh)
    previous_config = "/configurations/kh%.2f/" %(float(kh)-0.01)
    next_config = "/configurations/kh%.2f/" %(float(kh)+0.01)
    config_name = kh_val
    input_files = {'HELIAC (inner surfaces)':'/static/configdb/hin/gHg110324-kh%.3f-kv1.000.hin' %float(kh),
                   'HELIAC (outer surfaces)':'/static/configdb/hin/gHg110324-kh%.3f-kv1.000_outer.hin' %float(kh),
                   'VMEC input file':'/static/configdb/vmec/input.h1ass027v1_0p%02d' %(int(100*float(kh))),
                   'VMEC output (vacuum)':'/static/configdb/vmec/SCAN_FreeBound_VAC_NITER20000-2012-03-20/WOUT_LINKS/wout_VMEC_fb_kh%s.nc' %(kh_string_w_neg(float(kh))),
                   'VMEC output (0.1% beta)':'/static/configdb/vmec/SCAN_FreeBound_bav0.10-2012-03-22/WOUT_LINKS/wout_VMEC_fb_kh%s.nc' %(kh_string_w_neg(float(kh))),
                   'Boozer coordinates [NetCDF]':'/static/configdb/vmec/boozmn_h1ass027v1_0p%02d.nc' %(int(100*float(kh)))}

    if (10*float(kh)).is_integer():
        # only for 0.1 steps
        input_files['BLINE'] = '/static/configdb/bline/hnh3k%02d.txt' %(int(10*float(kh)))
        input_files['BLINE pre-computed magnetic mesh [NetCDF] (large file: 328Mb)'] = '/static/configdb/bline/hnh3k%02d.nc' %(int(10*float(kh)))
    figures = []
    figures.append({'name':'Rotational transform profile',
                    'image':'/static/configdb/iotabar/iotabar_kh%s_small.png' %kh_val,
                    'links':[{'name':'PNG (small)', 'url':'/static/configdb/iotabar/iotabar_kh%s_small.png' %kh_val},
                             {'name':'PNG (large)', 'url':'/static/configdb/iotabar/iotabar_kh%s_large.png' %kh_val},
                             {'name':'SVG', 'url':'/static/configdb/iotabar/iotabar_kh%s.svg' %kh_val},
                             ]}
                   )
    figures.append({'name':'Magnetic well profile',
                    'image':'/static/configdb/magwell/magwell_kh%s_small.png' %kh_val,
                    'links':[{'name':'PNG (small)', 'url':'/static/configdb/magwell/magwell_kh%s_small.png' %kh_val},
                             {'name':'PNG (large)', 'url':'/static/configdb/magwell/magwell_kh%s_large.png' %kh_val},
                             {'name':'SVG', 'url':'/static/configdb/magwell/magwell_kh%s.svg' %kh_val},
                             ]}
                   )

    for phi in range(0,121, 10):
        figures.append({'name':'Poincare plot (phi=%d)' %phi,
                        'image':'/static/configdb/poincare/kh%s-phi%d_small.png' %(kh_val, phi),
                        'links':[{'name':'PNG (small)', "url":'/static/configdb/poincare/kh%s-phi%d_small.png' %(kh_val, phi)},
                                 {'name':'PNG (large)', 'url':'/static/configdb/poincare/kh%s-phi%d_large.png' %(kh_val, phi)},
                                 {'name':'SVG', 'url':'/static/configdb/poincare/kh%s-phi%d.svg' %(kh_val, phi)},
                                 ]}
                       )
        
    return render_to_response('h1ds_configdb/configdb_kh_overview.html', {'config':config_name, 
                                                                          'figures':figures,
                                                                          'input_files':input_files,
                                                                          'next_config':next_config,
                                                                          'previous_config':previous_config},
                              context_instance=RequestContext(request),
                              )

"""

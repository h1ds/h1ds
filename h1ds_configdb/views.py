from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

def configdb_home(request):
    config_list = []
    for khx in range(0,121):
        kh = khx*0.01
        config_list.append({'name':'kh:%.2f, kv:1.00' %kh, 
                            'url':'/configurations/kh%.2f/' %kh, 
                            'kh':"%.2f" %kh, 'kv':"1.00"})

    return render_to_response('h1ds_configdb/configdb_home.html', {'configs':config_list},
                              context_instance=RequestContext(request),
                              )

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


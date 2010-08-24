# Create your views here.

from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Q

from h1ds_summary.models import Shot, SummaryAttribute, FloatAttributeInstance

def summary_overview(request):
    latest_shots = Shot.objects.order_by('-shot')[:5]
    summ_att = SummaryAttribute.objects.all()
    shot_list = []
    for s in latest_shots:
        tmp_s = [s.shot]
        for a in summ_att:
            try:
                tmp_val = a.get_att_class().objects.filter(shot=s,attribute=a)[0].value
            except:
                tmp_val = ''
            tmp_s.append(tmp_val)
        shot_list.append(tmp_s)
    attrs = [a.name for a in summ_att]
    return render_to_response('summary/overview.html', {'shots':shot_list, "attrs":attrs})

def get_last_n(number_of_shots):
    latest_shots = Shot.objects.order_by('-shot')[:number_of_shots]
    return [i.shot for i in latest_shots]

def process_shot_regex(shot_regex):
    shot_filter = Q()
    shot_ranges = shot_regex.split('+')
    for shot_range in shot_ranges:
        if shot_range.startswith("last"):
            last_shot = get_last_n(1)[0]
            if shot_range == "last":                
                shot_filter = shot_filter | Q(shot=last_shot)                
            else:
                shot_filter = shot_filter | (Q(shot__gt=(last_shot-int(shot_range[4:]))) & Q(shot__lte=int(last_shot)))
        else:
            limits = shot_range.split('-')
            if len(limits)==1:
                shot_filter = shot_filter | Q(shot=int(limits[0]))
            else:
                shot_filter = shot_filter | (Q(shot__gte=int(limits[0])) & Q(shot__lte=int(limits[1])))
    return shot_filter


def shot_overview(request, shot_regex):
    shot_filter = process_shot_regex(shot_regex)
    shots = Shot.objects.filter(shot_filter).order_by('-shot')
    summ_att = SummaryAttribute.objects.all()
    shot_list = []
    for s in shots:
        tmp_s = [s.shot]
        for a in summ_att:
            try:
                tmp_val = a.get_att_class().objects.filter(shot=s,attribute=a)[0].value
            except:
                tmp_val = ''
            tmp_s.append(tmp_val)
        shot_list.append(tmp_s)
    attrs = [a.name for a in summ_att]
    return render_to_response('summary/overview.html', {'shots':shot_list, "attrs":attrs})

def process_data_regex(data_regex):
    attr_list = data_regex.split('+')
    return attr_list

def shot_data_overview(request, shot_regex, data_regex):
    shot_list = process_shot_regex(shot_regex)
    attr_list = process_data_regex(data_regex)
    latest_shots = Shot.objects.filter(shot__in=shot_list).order_by('-shot')
    summ_att = SummaryAttribute.objects.filter(slug__in=attr_list)
    shot_list = []
    for s in latest_shots:
        tmp_s = [s.shot]
        for a in summ_att:
            try:
                tmp_val = a.get_att_class().objects.filter(shot=s,attribute=a)[0].value
            except:
                tmp_val = ''
            tmp_s.append(tmp_val)
        shot_list.append(tmp_s)
    attrs = [a.name for a in summ_att]
    return render_to_response('summary/overview.html', {'shots':shot_list, "attrs":attrs})

def process_filter_regex(filter_regex):
    filter_str_list = filter_regex.split('+')
    filter_list = []
    for f in filter_str_list:
        fstr = f.split('__')
        tmp_f = [SummaryAttribute.objects.get(slug=fstr[0]), fstr[1]]
        tmp_f.extend(map(tmp_f[0].get_datatype(), fstr[2:]))
        filter_list.append(tmp_f)
    return filter_list


def check_filter_list(shot_number, filter_list):
    return_value = True
    for f in filter_list:
        if check_filter(shot_number, f)==False:
            return_value = False
    return return_value

def check_filter(shot_number, filter_info):
    attr_value = filter_info[0].get_value(shot_number)
    return_val = False
    if filter_info[1] == 'gt':
        if attr_value > filter_info[2]:
            return_val = True
    return return_val

def shot_data_filter_overview(request, shot_regex, data_regex, filter_regex):
    shot_list = process_shot_regex(shot_regex)
    attr_list = process_data_regex(data_regex)
    latest_shots = Shot.objects.filter(shot__in=shot_list).order_by('-shot')
    summ_att = SummaryAttribute.objects.filter(slug__in=attr_list)
    filters = process_filter_regex(filter_regex)
    shot_list = []
    for s in latest_shots:
        if check_filter_list(s.shot, filters):
            tmp_s = [s.shot]
            for a in summ_att:
                try:
                    tmp_val = a.get_att_class().objects.filter(shot=s,attribute=a)[0].value
                except:
                    tmp_val = ''
                tmp_s.append(tmp_val)
            shot_list.append(tmp_s)
    attrs = [a.name for a in summ_att]
    return render_to_response('summary/overview.html', {'shots':shot_list, "attrs":attrs})

"""
def shot_overview(request, shot_regex):
    shot_list = process_shot_regex(shot_regex)
    s = get_object_or_404(Shot, shot=shot_list[0])
    summ_att = SummaryAttribute.objects.all()
    attrs = []
    for a in summ_att:
        try:
            tmp_val = a.get_att_class().objects.filter(shot=s,attribute=a)[0].value
        except:
            tmp_val = ''
        attrs.append([a,tmp_val])
    return render_to_response('summary/shot_overview.html', {'shot':s, "attrs":attrs})
    
"""

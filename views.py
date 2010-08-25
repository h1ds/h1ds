# Create your views here.

from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Q

from h1ds_summary.models import Shot, SummaryAttribute, FloatAttributeInstance

def do_html_data(data, attr_list):
    output_data = []
    for row in data:
        row_data = [row[0]]
        for attr_i,attr_data in enumerate(row[1:]):
            attr_value = attr_data
            if attr_list[attr_i].display_format:
                try:
                    attr_value = attr_list[attr_i].display_format %(attr_data)
                except:
                    pass
            row_data.append({'val':attr_value, 'norm':int(100.0*attr_list[attr_i].normalise(attr_data)), 'col':attr_list[attr_i].colourise(attr_data)})
        output_data.append(row_data)
    return output_data

def overview(request, shot_regex="last10", data_regex="all", filter_regex=None):
    [data,attr_list] = Shot.objects.summarydata(shot_regex, attr_query=data_regex, filter_query=filter_regex)
    html_data = do_html_data(data, attr_list)
    return render_to_response('summary/overview.html', {'data':html_data, 'attrs':attr_list})

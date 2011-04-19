from django.shortcuts import render_to_response
from django.template import RequestContext


def homepage(request):
    """Return the H1DS homepage."""
    return render_to_response('h1ds_core/homepage.html', 
                              context_instance=RequestContext(request))

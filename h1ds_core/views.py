from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.core import serializers
from django.http import HttpResponse
from django.contrib.auth import logout
    
from h1ds_core.models import H1DSSignalInstance

def homepage(request):
    """Return the H1DS homepage."""
    return render_to_response('h1ds_core/homepage.html', 
                              context_instance=RequestContext(request))

def dashboard(request):
    """Return the H1DS homepage."""
    signals = H1DSSignalInstance.objects.all()[:20]
    if request.is_ajax():
        signals_json = serializers.serialize('json', reversed(signals), use_natural_keys=True)
        return HttpResponse(signals_json, 'application/javascript')
    return render_to_response('h1ds_core/dashboard.html',{'signals':signals}, 
                              context_instance=RequestContext(request))


def logout_view(request):
    """Log the user out of H1DS."""
    logout(request)
    return redirect('/')
            

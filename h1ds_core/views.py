from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.core import serializers
from django.http import HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django import forms
    
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
            

class ChangeProfileForm(forms.Form):
    username = forms.CharField(max_length=30, help_text="Please use CamelCase, with each word capitalised. For example: MarkOliphant or LymanSpitzer")
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()


@login_required
def edit_profile(request, username=''):
    if request.user.username == username:
        if request.method == 'POST':
            form = ChangeProfileForm(request.POST)
            if form.is_valid():
                u = User.objects.get(username=username)
                u.username = form.cleaned_data['username']
                u.first_name = form.cleaned_data['first_name']
                u.last_name = form.cleaned_data['last_name']
                u.email = form.cleaned_data['email']
                u.save()
                return redirect('/')
                
            else:
                data = {'username':username, 
                        'first_name':request.user.first_name,
                        'last_name':request.user.last_name,
                        'email':request.user.email}
                user_form = ChangeProfileForm(data)
                return render_to_response('h1ds_core/userprofile.html', 
                                          {'form':user_form, 'return_url':'/user/profile/%s/' %username},
                                          context_instance=RequestContext(request))
        else:
            data = {'username':username, 
                    'first_name':request.user.first_name,
                    'last_name':request.user.last_name,
                    'email':request.user.email}
            user_form = ChangeProfileForm(data)
            return render_to_response('h1ds_core/userprofile.html', 
                                      {'form':user_form},
                                      context_instance=RequestContext(request))
    else:
        return redirect('/')



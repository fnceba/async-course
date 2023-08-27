from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render

from ates_auth.forms import AuthForm
from ates_auth.models import User

# Create your views here.

def v_auth(request):
    auth_form = AuthForm()
    if request.method == 'POST':
        auth_form = AuthForm(request.POST)
        if auth_form.is_valid():
            email = auth_form.cleaned_data['email']
            password = auth_form.cleaned_data['password']
            if token:=User.get_user_token(email, password):
                redirect_to = request.GET.get('next')
                if redirect_to:
                    response = HttpResponseRedirect(redirect_to)
                else:
                    response = render(request, 'auth.html', dict(is_authorized = True, token = token))
                response.set_cookie('token', token)
                return response
            else:
                return render(request, 'auth.html', dict(auth_form=auth_form, warning = 'Invalid Credentials'))
    return render(request, 'auth.html', dict(auth_form=auth_form))

def v_parse_token(request):
    return HttpResponse(User.parse_user_token(request.body))
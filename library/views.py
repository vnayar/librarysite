from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render


def index(request):
    context = {}
    return render(request, 'library/home.html', context)


def login_view(request):
    if request.method == 'POST': # If the form has been submitted...
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect("/library/")
            else:
                # Return a 'disabled account' error message
                return HttpResponse("Disabled Account!")
        else:
            # Return an 'invalid login' error message.
            return HttpResponse("Invalid Login!")
    else:
        form = AuthenticationForm() # An unbound form

    return render(request, 'library/login.html', { 'form': form })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/library/")

@login_required
def dashboard_view(request):
    context = {}
    return render(request, 'library/dashboard.html', context)

@login_required
def admin_view(request):
    context = {}
    return render(request, 'library/admin.html', context)

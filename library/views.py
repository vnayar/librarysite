from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render


def index(request):
    context = {}
    return render(request, 'library/home.html', context)


def login(request):
    if request.method == 'POST': # If the form has been submitted...
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request)
                return HttpResponseRedirect("/library/main.html")
            else:
                # Return a 'disabled account' error message
                return HttpResponse("Disabled Account!")
        else:
            # Return an 'invalid login' error message.
            return HttpResponse("Invalid Login!")
    else:
        form = AuthenticationForm() # An unbound form

    return render(request, 'library/login.html', {
        'form': form,
    })

    






from django import forms
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from .models import Reader


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

@login_required
def admin_reader(request):
    readers = Reader.objects.all()
    context = { "readers" : readers }
    return render(request, 'library/admin_reader.html', context)

@login_required
def admin_reader(request):
    readers = Reader.objects.all()
    context = { "readers" : readers }
    return render(request, 'library/admin_reader.html', context)


class ReaderForm(forms.Form):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    address = forms.CharField()
    phone_number = forms.CharField(max_length=20)
    

@login_required
def admin_reader_add(request):
    if request.method == 'POST':
        # Handle form submission.
        form = ReaderForm(request.POST) # Initialize form with data.
        if form.is_valid():
            
            # First create a new User object.
            user = User()
            # Process the data in form.cleaned_data
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            # New create a reader object.
            reader = Reader()
            reader.user = user
            reader.address = form.cleaned_data['address']
            reader.phone_number = form.cleaned_data['phone_number']
            reader.save()
            
            return HttpResponseRedirect(reverse('admin_reader')) # Redirect after POST
    else:
        form = ReaderForm() # An unbound form

    return render(request, 'library/admin_reader_add.html', {
        'form': form,
    })

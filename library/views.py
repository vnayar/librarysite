from datetime import datetime
import pytz

from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render

from .models import Reader, Book, BookCopy, LibraryBranch

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
@staff_member_required
def admin_view(request):
    context = {}
    return render(request, 'library/admin.html', context)

@login_required
@staff_member_required
def admin_librarybranch(request):
    page = int(request.GET.get('page', '1'))
    limit = 10
    offset = limit * (page - 1)

    librarybranch_list = LibraryBranch.objects.all()[offset : offset + limit]
    page_count = LibraryBranch.objects.count() / limit + 1
    context = {
        "librarybranch_list" : librarybranch_list,
        "page_count" : page_count,
        "page" : page,
        "pages" : range(1, page_count + 1),
        "page_prev" : max(page - 1, 1),
        "page_next" : min(page + 1, page_count)
        }
    return render(request, 'library/admin_librarybranch.html', context)

@login_required
@staff_member_required
def admin_reader(request):
    page = int(request.GET.get('page', '1'))
    limit = 10
    offset = limit * (page - 1)

    reader_list = Reader.objects.all()[offset : offset + limit]
    page_count = Reader.objects.count() / limit + 1
    context = {
        "reader_list" : reader_list,
        "page_count" : page_count,
        "page" : page,
        "pages" : range(1, page_count + 1),
        "page_prev" : max(page - 1, 1),
        "page_next" : min(page + 1, page_count)
        }
    return render(request, 'library/admin_reader.html', context)


class ReaderForm(forms.Form):
    """
    Form for adding a new Reader.
    """
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    address = forms.CharField()
    phone_number = forms.CharField(max_length=20)
    

@login_required
@staff_member_required
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

@login_required
@staff_member_required
def admin_bookcopy(request):
    page = int(request.GET.get('page', '1'))
    limit = 10
    offset = limit * (page - 1)

    bookcopy_list = BookCopy.objects.all()[offset : offset + limit]
    page_count = BookCopy.objects.count() / limit + 1
    context = {
        "bookcopy_list" : bookcopy_list,
        "page_count" : page_count,
        "page" : page,
        "pages" : range(1, page_count + 1),
        "page_prev" : max(page - 1, 1),
        "page_next" : min(page + 1, page_count)
        }
    return render(request, 'library/admin_bookcopy.html', context)

class BookCopyForm(forms.Form):
    """
    Form for adding a new BookCopy.
    """
    library_branch = forms.ChoiceField(label="Library Branch",
                                       choices=(),
                                       widget=forms.Select())
    book = forms.ChoiceField(label="Book",
                             choices=(),
                             widget=forms.Select())
    copy_number = forms.IntegerField(label="Copy Number", min_value=1)
    position = forms.CharField(max_length=30)

    def __init__(self, *args, **kwargs):
        super(BookCopyForm, self).__init__(*args, **kwargs)
        library_branch_choices = [(lb.id, lb.name) for lb in LibraryBranch.objects.all()]
        self.fields['library_branch'].choices = library_branch_choices
        book_choices = [(b.id, b.title[0:40]) for b in Book.objects.all()]
        self.fields['book'].choices = book_choices


@login_required
@staff_member_required
def admin_bookcopy_add(request):
    if request.method == 'POST':
        # Handle form submission.
        form = BookCopyForm(request.POST) # Initialize form with data.
        if form.is_valid():
            bookcopy = BookCopy()
            bookcopy.book = Book.objects.get(
                id=form.cleaned_data['book'])
            bookcopy.library_branch = LibraryBranch.objects.get(
                id=form.cleaned_data['library_branch'])
            bookcopy.copy_number = form.cleaned_data['copy_number']
            bookcopy.position = form.cleaned_data['position']
            bookcopy.save()
            return HttpResponseRedirect(reverse('admin_bookcopy')) # Redirect after POST
    else:
        form = BookCopyForm() # An unbound form

    return render(request, 'library/admin_bookcopy_add.html', {
        'form': form,
    })

@login_required
def dashboard_view(request):
    context = {}
    return render(request, 'library/dashboard.html', context)

@login_required
def reader_bookcopy(request):
    page = int(request.GET.get('page', '1'))
    limit = 10
    offset = limit * (page - 1)

    bookcopy_list = []
    query = request.GET.get('q', None)
    search_by = request.GET.get('by', None)
    if query:
        if search_by == 'title':
            print "Filtering on title"
            bookcopy_list = BookCopy.objects.filter(book__title__icontains=query)
        elif search_by == 'isbn':
            print "Filtering on isbn"
            bookcopy_list = BookCopy.objects.filter(book__isbn__icontains=query)
        elif search_by == 'publisher':
            print "Filtering on publisher"
            bookcopy_list = BookCopy.objects.filter(book__publisher__name__icontains=query)
    else:
        bookcopy_list = BookCopy.objects.all()

    page_count = len(bookcopy_list) / limit + 1
    bookcopy_list = bookcopy_list[offset : offset + limit]
    context = {
        "query" : query,
        "search_by" : search_by,
        "bookcopy_list" : bookcopy_list,
        "page_count" : page_count,
        "page" : page,
        "pages" : range(1, page_count + 1),
        "page_prev" : max(page - 1, 1),
        "page_next" : min(page + 1, page_count)
        }
    return render(request, 'library/reader_bookcopy.html', context)

class BookCopyCheckoutForm(forms.Form):
    id = forms.IntegerField(label='ID', widget=forms.HiddenInput())
    title = forms.CharField(
        widget=forms.TextInput(attrs={'readonly':'readonly'}))
    authors = forms.CharField(
        widget=forms.TextInput(attrs={'readonly':'readonly'}))
    status = forms.CharField(required=False,
        widget=forms.TextInput(attrs={'readonly':'readonly'}))


    ACTION_CHOICES = (('checkout', 'Checkout',), ('reserve', 'Reserve',))
    action = forms.ChoiceField(widget=forms.RadioSelect, choices=ACTION_CHOICES)

    def __init__(self, bookcopy, status, *args, **kwargs):
        super(BookCopyCheckoutForm, self).__init__(*args, **kwargs)
        if bookcopy:
            self.fields['id'].initial = bookcopy.id
            self.fields['title'].initial = bookcopy.book.title
            # Combine all the authors into a comma separated list.
            self.fields['authors'].initial = reduce(
                lambda author_string, author: author_string + author.name + ", ",
                bookcopy.book.authors.all(),
                "")
            if status:
                self.fields['status'].initial = status

@login_required
def reader_checkout(request):
    bookcopy = None
    if request.method == 'POST':
        form = BookCopyCheckoutForm(None, None, request.POST)
        if form.is_valid():
            id = form.cleaned_data['id']
            action = form.cleaned_data['action']
            bookcopy = BookCopy.objects.get(id=id)
            bookcopy.user = request.user
            now = datetime.now(pytz.utc)
            if bookcopy.is_available(request.user, now):
                if action == 'checkout':
                    bookcopy.borrow_date = now
                elif action == 'reserve':
                    bookcopy.reserve_date = now
                bookcopy.save()
            else:
                return HttpResponse("Book is not available!")
            return HttpResponseRedirect(reverse('reader_bookcopy')) # Redirect after POST
    else:
        id = int(request.GET.get('id', None))
        if not id:
            raise Http404
        bookcopy = BookCopy.objects.get(id=id)
        status = bookcopy.status(request.user, datetime.now(pytz.utc))
        form = BookCopyCheckoutForm(bookcopy, status)

    context = {
        "bookcopy" : bookcopy,
        "form" : form
        }
    return render(request, 'library/reader_checkout.html', context)


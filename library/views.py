from datetime import datetime, timedelta
import pytz

from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Avg, Max, Min, Count
from django.db import connection
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render

from .models import Reader, Book, BookCopy, BookCopyCheckout, LibraryBranch

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
    username = forms.CharField(max_length=20)
    password = forms.CharField(max_length=20)
    

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
            user.username = form.cleaned_data['username']
            user.password = make_password(form.cleaned_data['password'])
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

class LibraryBranchStatisticsForm(forms.Form):
    """
    Form for requesting statistics about a LibraryBranch.
    """
    library_branch = forms.ChoiceField(label="Library Branch",
                                       choices=(),
                                       widget=forms.Select())
    
    STATISTIC_CHOICES = (
        ('borrow', 'Top Borrowers',),
        ('books', 'Top Books',),
        ('avg_fine', 'Average Fine',))
    statistic = forms.ChoiceField(label="Statistic",
                                  choices=STATISTIC_CHOICES,
                                  widget=forms.Select())

    def __init__(self, *args, **kwargs):
        super(LibraryBranchStatisticsForm, self).__init__(*args, **kwargs)
        library_branch_choices = [(lb.id, lb.name) for lb in LibraryBranch.objects.all()]
        self.fields['library_branch'].choices = library_branch_choices

@login_required
@staff_member_required
def admin_librarybranch_statistics(request):
    if request.method == 'POST':
        # Handle form submission.
        form = LibraryBranchStatisticsForm(request.POST) # Initialize form with data.
        if form.is_valid():
            library_branch = LibraryBranch.objects.get(
                id=form.cleaned_data['library_branch'])
            statistic = form.cleaned_data['statistic']

            # Data for displaying a table.
            headers = []
            data = [[3, 4], [5, 6]]
            
            # Based upon the requested statistic, do the computations.
            if statistic == 'borrow':
                title = "Top Borrowers"
                headers = ['Username', 'Total Books Borrowed']
                data = BookCopyCheckout.objects \
                    .filter(bookcopy__library_branch=library_branch) \
                    .values_list('user__username') \
                    .annotate(num_books=Count('id')) \
                    .order_by('-num_books')
            elif statistic == 'books':
                title = "Top Borrowed Books"
                headers = ['Book Title', 'Times Borrowed']
                data = BookCopyCheckout.objects \
                    .filter(bookcopy__library_branch=library_branch) \
                    .values_list('bookcopy__book__title') \
                    .annotate(borrow_count=Count('id')) \
                    .order_by('-borrow_count')
            elif statistic == 'avg_fine':
                title = "Average Fine"
                headers = ['Average Fine']
                # Get a raw SQL connection to compute the average.
                # There's no easy Django equivalent for this.
                cursor = connection.cursor()
                cursor.execute(
                    '\n'.join([
                            'SELECT avg(late_days)',
                            'FROM (',
                            '  SELECT DateDiff(COALESCE(return_date, now()), borrow_date)',
                            '    - %s AS late_days',
                            '  FROM library_bookcopycheckout as bcc, library_bookcopy as bc',
                            '  WHERE bcc.bookcopy_id = bc.id',
                            '    AND bc.library_branch_id = %s',
                            '    AND not isnull(borrow_date)',
                            '  ) AS t1',
                            'WHERE late_days > 0']),
                    [20, library_branch.id]) # Fines are computed when late more than 20 days.
                avg_late_days = float(cursor.fetchone()[0])
                data = [['$%.2f' % (avg_late_days * 0.20)]] # 20 cents per day.
                print "data = ", data

            return render(request, 'library/admin_librarybranch_statistics.html', {
                    'form': form,
                    'library_branch' : library_branch,
                    'title' : title,
                    'headers' : headers,
                    'data' : data
                    })
        else:
            return HttpResponse("Invalid form!")
    else:
        form = LibraryBranchStatisticsForm() # An unbound form
        return render(request, 'library/admin_librarybranch_statistics.html', {
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

    bookcopy_set = BookCopy.objects
    bookcopy_list = []

    query = request.GET.get('q', None)
    search_by = request.GET.get('by', None)
    if search_by == 'mine':
        bookcopy_set = bookcopy_set.filter(current_checkout__user=request.user)
    elif query:
        if search_by == 'title':
            print "Filtering on title"
            bookcopy_set = bookcopy_set.filter(book__title__icontains=query)
        elif search_by == 'isbn':
            print "Filtering on isbn"
            bookcopy_set = bookcopy_set.filter(book__isbn__icontains=query)
        elif search_by == 'publisher':
            print "Filtering on publisher"
            bookcopy_set = bookcopy_set.filter(book__publisher__name__icontains=query)

    # Used for finding the status.
    now = datetime.now(pytz.utc)

    bookcopy_list = []
    for bookcopy in bookcopy_set.all():
        bookcopy_list.append({
                "id" : bookcopy.id,
                "library_branch_name" : bookcopy.library_branch.name,
                "copy_number" : bookcopy.copy_number,
                "position": bookcopy.position,
                "title" : bookcopy.book.title,
                "isbn" : bookcopy.book.isbn,
                "publisher_name" : bookcopy.book.publisher.name,
                "status" : bookcopy.status(request.user, now)
                })

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

@login_required
def reader_mybooks(request):
    page = int(request.GET.get('page', '1'))
    limit = 10
    offset = limit * (page - 1)

    bookcopy_list = []
    bookcopy_set = BookCopy.objects.filter(current_checkout__user=request.user)

    # Used for finding the status.
    now = datetime.now(pytz.utc)

    bookcopy_list = []
    for bookcopy in bookcopy_set.all():
        return_by_date = None
        fine = bookcopy.current_checkout.get_fine(now)
        if fine:
            fine = '$%.2f' % fine
        bookcopy_list.append({
                "id" : bookcopy.id,
                "library_branch_name" : bookcopy.library_branch.name,
                "copy_number" : bookcopy.copy_number,
                "title" : bookcopy.book.title,
                "reserve_date" : bookcopy.current_checkout.reserve_date or "--",
                "borrow_date" : bookcopy.current_checkout.borrow_date or "--",
                "return_by_date" : return_by_date or "--",
                "status" : bookcopy.status(request.user, now),
                "fine" : fine or "--"
                })

    page_count = len(bookcopy_list) / limit + 1
    bookcopy_list = bookcopy_list[offset : offset + limit]
    context = {
        "bookcopy_list" : bookcopy_list,
        "page_count" : page_count,
        "page" : page,
        "pages" : range(1, page_count + 1),
        "page_prev" : max(page - 1, 1),
        "page_next" : min(page + 1, page_count)
        }
    return render(request, 'library/reader_mybooks.html', context)

class BookCopyCheckoutForm(forms.Form):
    id = forms.IntegerField(label='ID', widget=forms.HiddenInput())
    # Some informational fields so the user knows what they are checking out.
    title = forms.CharField(
        widget=forms.TextInput(attrs={'readonly':'readonly'}))
    authors = forms.CharField(
        widget=forms.TextInput(attrs={'readonly':'readonly'}))
    status = forms.CharField(required=False,
        widget=forms.TextInput(attrs={'readonly':'readonly'}))


    ACTION_CHOICES = (
        ('borrow', 'Borrow',),
        ('reserve', 'Reserve',),
        ('return', 'Return',))
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
    """
    A form used by the reader to borrow, reserve, or return a book.
    """
    bookcopy = None
    if request.method == 'POST':

        # A 'POST' request is for form submission.
        form = BookCopyCheckoutForm(None, None, request.POST)
        if form.is_valid():
            id = form.cleaned_data['id']
            action = form.cleaned_data['action']
            now = datetime.now(pytz.utc)
            bookcopy = BookCopy.objects.get(id=id)

            if action == 'borrow' or action == 'reserve':
                # Make sure the user does not check out more than 10 books at a time.
                checkout_count = len(filter(
                        lambda checkout: checkout.is_current(now),
                        BookCopyCheckout.objects.filter(user=request.user)))
                if checkout_count > 10:
                    return HttpResponse("User may not borrow or reserve more than 10 books!")

                # Now perform the requested action.
                if bookcopy.is_available(request.user, now):
                    if action == 'borrow':
                        bookcopy.do_borrow(request.user, now)
                    elif action == 'reserve':
                        bookcopy.do_reserve(request.user, now)
                else:
                    return HttpResponse("Book is not available!")
            elif action == 'return':
                # The book does not need to be 'available' to return it.
                bookcopy.do_return(request.user, now)

            return HttpResponseRedirect(reverse('reader_bookcopy')) # Redirect after POST
    else:
        # A 'GET' request is to view the form.
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


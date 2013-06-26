from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Author(models.Model):
    """
    Data about authors of books.
    """
    name = models.CharField(max_length=200)

class Publisher(models.Model):
    """
    Data about a publishing business that prints book copies.
    """
    name = models.CharField(max_length=200)
    address = models.TextField()

class Book(models.Model):
    """
    Summary information about a book.
    """
    title = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13)
    publisher = models.ForeignKey(Publisher)
    publication_date = models.DateTimeField()

class BookAuthor(models.Model):
    """
    Association between books and authors.
    """
    book = models.ForeignKey(Book)
    author = models.ForeignKey(Author)

class LibraryBranch(models.Model):
    """
    A building that holds and keeps track of books.
    """
    name = models.CharField(max_length=200)
    address = models.TextField()

class Reader(models.Model):
    """
    A person who may check books out from the library.
    """
    user = models.ForeignKey(User)
    address = models.TextField()
    phone_number = models.CharField(max_length=20)

class BookCopy(models.Model):
    """
    A physical copy of a book that may be lent out.
    """
    book = models.ForeignKey(Book)
    library_branch = models.ForeignKey(LibraryBranch)
    copy_number = models.IntegerField()
    position = models.CharField(max_length=6)

    # Information about who/when the book was borrowed.
    reader = models.ForeignKey(Reader, null=True)
    borrow_date = models.DateTimeField(null=True)
    return_date = models.DateTimeField(null=True)

    # Meta-options of the model.
    unique_together = ('book', 'library_branch', 'copy_number')

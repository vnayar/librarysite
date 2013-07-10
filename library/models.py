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
    publication_date = models.DateField()
    authors = models.ManyToManyField(Author)

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
    position = models.CharField(max_length=6, unique=True)

    # Information about who/when the book was borrowed.
    user = models.ForeignKey(User, null=True)
    reserve_date = models.DateTimeField(null=True)
    borrow_date = models.DateTimeField(null=True)
    return_date = models.DateTimeField(null=True)

    # Meta-options of the model.
    unique_together = ('book', 'library_branch', 'copy_number')

    def is_available(self, user, datetime):
        """
        Determine if a book is currenty available for checkout.
        """
        if self.user == None:
            return True
        if self.return_date and self.return_date < datetime:
            return True
        if self.borrow_date and self.borrow_date < datetime:
            return False
        if self.reserve_date and self.reserve_date < datetime and self.user != user:
            return False
        return True

    def status(self, user, datetime):
        """
        Determine if a book is currenty available for checkout.
        """
        if self.user == None:
            return 'available'
        if self.return_date and self.return_date < datetime:
            return 'available'
        if self.borrow_date and self.borrow_date < datetime:
            return 'loaned'
        if self.reserve_date and self.reserve_date < datetime:
            if self.user == user:
                return 'reserved (you)'
            else:
                return 'reserved (other)'
        return 'available'


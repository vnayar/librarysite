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

    # A reference to the current checkout status of the book.
    current_checkout = models.ForeignKey('BookCopyCheckout',
                                         related_name='current_checkout',
                                         null=True)

    # Meta-options of the model.
    unique_together = ('book', 'library_branch', 'copy_number')

    def is_available(self, user, datetime):
        """
        Determine if a book is currenty available for checkout.
        """
        checkout = self.current_checkout
        if checkout == None:
            return True
        if checkout.return_date and checkout.return_date < datetime:
            return True
        if checkout.borrow_date and checkout.borrow_date < datetime:
            return False
        if checkout.reserve_date and checkout.reserve_date < datetime and checkout.user != user:
            return False
        return True

    def status(self, user, datetime):
        """
        Determine if a book is currenty available to borrow.
        """
        checkout = self.current_checkout
        if checkout == None:
            return 'available'
        if checkout.return_date and checkout.return_date < datetime:
            return 'available'
        if checkout.borrow_date and checkout.borrow_date < datetime:
            return 'loaned'
        if checkout.reserve_date and checkout.reserve_date < datetime:
            if checkout.user == user:
                return 'reserved (you)'
            else:
                return 'reserved (other)'
        return 'available'

    def do_borrow(self, user, datetime):
        """
        Update records for a user to borrow a book.
        """
        if not self.is_available(user, datetime):
            raise ValueError("Book is not available!")
        if self.current_checkout and user == self.current_checkout.user:
            self.current_checkout.borrow_date = datetime
            self.current_checkout.save()
        else:
            checkout = BookCopyCheckout(user=user, bookcopy=self, borrow_date=datetime)
            checkout.save()
            self.current_checkout = checkout
            self.save()

    def do_reserve(self, user, datetime):
        """
        Update records for a user to reserve a book.
        """
        if not self.is_available(user, datetime):
            raise ValueError("Book is not available!")
        if self.current_checkout and user == self.current_checkout.user:
            self.current_checkout.reserve_date = datetime
            self.current_checkout.save()
        else:
            checkout = BookCopyCheckout(user=user, bookcopy=self, reserve_date=datetime)
            checkout.save()
            self.current_checkout = checkout
            self.save()

    def do_return(self, user, datetime):
        """
        Update records for a user to return a book.
        """
        if self.current_checkout and self.current_checkout.borrow_date:
            self.current_checkout.return_date = datetime
            self.current_checkout.save()
            self.current_checkout = None
            self.save()
        else:
            raise ValueError("Book was not borrowed!")

class BookCopyCheckout(models.Model):
    """
    Separate information describing a book being checked out.
    """
    # Information about who/when the book was borrowed.
    user = models.ForeignKey(User)
    bookcopy = models.ForeignKey(BookCopy)
    reserve_date = models.DateTimeField(null=True)
    borrow_date = models.DateTimeField(null=True)
    return_date = models.DateTimeField(null=True)


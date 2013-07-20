from datetime import date, datetime, timedelta

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
    name = models.CharField(max_length=200, unique=True)
    address = models.TextField()

class Book(models.Model):
    """
    Summary information about a book.
    """
    title = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    publisher = models.ForeignKey(Publisher)
    publication_date = models.DateField()
    authors = models.ManyToManyField(Author)

class LibraryBranch(models.Model):
    """
    A building that holds and keeps track of books.
    """
    name = models.CharField(max_length=200, unique=True)
    address = models.TextField()

class Reader(models.Model):
    """
    A person who may check books out from the library.
    """
    user = models.ForeignKey(User, unique=True)
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

    def is_available(self, user, now):
        """
        Determine if a book is currenty available for checkout.
        """
        checkout = self.current_checkout
        if checkout == None:
            return True
        if not checkout.is_current(now):
            # Erase the current_checkout if it is no longer valid.
            self.current_checkout = None
            self.save()
            return True
        # At this point, there must be a checkout that is current.
        if checkout.reserve_date and checkout.user == user and not checkout.borrow_date:
            # The user may borrow a book they have reserved.
            return True
        return False

    def status(self, user, now):
        """
        Determine if a book is currenty available to borrow.
        """
        checkout = self.current_checkout
        if self.is_available(user, now):
            if checkout and checkout.reserve_date:
                return 'reserved (mine)'
            else:
                return 'available'
        # If the book is not available, then there is a current_checkout.
        if checkout.borrow_date:
            if checkout.user == user:
                return 'borrowed (mine)'
            else:
                return 'borrowed'
        if checkout.reserve_date:
            return 'reserved'
        raise ValueError("BookCopy current_checkout in bad state!")

    def do_borrow(self, user, now):
        """
        Update records for a user to borrow a book.
        """
        if not self.is_available(user, now):
            raise ValueError("Book is not available!")
        if self.current_checkout and self.current_checkout.user == user:
            # Checkout exists (a reservation), so update it.
            self.current_checkout.borrow_date = now
            self.current_checkout.save()
        else:
            # Create a new checkout.
            checkout = BookCopyCheckout(user=user, bookcopy=self, borrow_date=now)
            checkout.save()
            self.current_checkout = checkout
            self.save()

    def do_reserve(self, user, now):
        """
        Update records for a user to reserve a book.
        """
        if not self.is_available(user, now):
            raise ValueError("Book is not available!")
        if self.current_checkout and self.current_checkout.user == user:
            self.current_checkout.reserve_date = now
            self.current_checkout.save()
        else:
            checkout = BookCopyCheckout(user=user, bookcopy=self, reserve_date=now)
            checkout.save()
            self.current_checkout = checkout
            self.save()

    def do_return(self, user, now):
        """
        Update records for a user to return a book.
        """
        if self.current_checkout and self.current_checkout.borrow_date:
            self.current_checkout.return_date = now
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

    def is_current(self, now):
        """
        Determine if a checkout 'current' at a particular time.
        A checkout is current if it solely determines the status of the book.
        """
        if self.return_date and self.return_date < now:
            # Book has been returned, this checkout is not current.
            return False
        elif self.borrow_date and self.borrow_date < now:
            # If there is a borrow date and no return, then it is current.
            return True
        elif self.reserve_date:
            # See if the reserve has expired (6PM the day of the reservation).
            reserve_expire_date = datetime(tzinfo=self.reserve_date.tzinfo,
                year=self.reserve_date.year, month=self.reserve_date.month,
                day=self.reserve_date.day, hour=18)
            if self.reserve_date.hour >= reserve_expire_date.hour:
                reserve_expire_date.day += 1
            if now > reserve_expire_date:
                return False
            else:
                return True
        # No date information at all.
        return False

    def get_fine(self, now):
        """
        If a fine is applicable, compute it as a floating point number.
        The fine is 20 cents per day, if there is no fine, the value
        None is returned.
        @return Float | None
        """
        if self.borrow_date:
            return_by_date = self.borrow_date + timedelta(days=20)
            if now > return_by_date:
                return (20 * (now - return_by_date).days) / 100.0
        return None



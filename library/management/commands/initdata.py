from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import IntegrityError

from library.models import (Author, Publisher, Book, LibraryBranch,
                            Reader, BookCopy)

from datetime import date
import random
import string

class Command(BaseCommand):
    args = '<none>'
    help = 'Generates initial data for the library database.'

    def handle(self, *args, **options):
        
        random.seed()

        self.init_author()
        self.stdout.write('Successfully created authors.')

        self.init_publisher()
        self.stdout.write('Successfully created publishers.')

        self.init_book()
        self.stdout.write('Successfully created books.')

        self.init_librarybranch()
        self.stdout.write('Successfully created library branches.')

        self.init_reader()
        self.stdout.write('Successfully created readers.')

        self.init_bookcopy()
        self.stdout.write('Successfully created book copies.')


    def rand_join(self, char, *args):
        """
        Pick random array string entires and concatenate them as a string.
        @param char:string
        @param args:Array<string>
        @return string
        """
        results = []
        for arg in args:
            results.append(arg[random.randint(0, len(arg) - 1)])
        return char.join(results)

    def init_author(self):
        # Remove existing Author models from the DB.
        Author.objects.all().delete()

        first_names = ["Fred", "George", "Juan", "Pablo", "Rohit", "Graham", "Jessica"]
        last_names = ["Salvador", "Gonzales", "Miller", "Walker", "Crofford", "Adams"]
        for i in range(1, 100):
            # Create a random name for the author.
            name = self.rand_join(' ', first_names, last_names)
            # Save the author in the DB.
            author = Author(name=name)
            author.save()

    def init_publisher(self):
        for i in range(1, 10):
            name = self.rand_join(' ',
                                  ["Wesley", "O'Reilly", "Oxford", "Stanley"],
                                  ["Press", "Printing", "Publishing", "Inc."])

            address = self.rand_join(' ',
                                     ["101", "45", "89", "412", "160"],
                                     ["Harold", "Lexinton", "Houston", "Broadway", "Main"],
                                     ["Drive", "Avenue", "Parkway", "Place", "Lane"])
            # Save the publisher in the DB.
            publisher = Publisher(name=name, address=address)
            try:
                publisher.save()
            except IntegrityError:
                # Try again.
                i -= 1

    def init_book(self):
        # Define a boundary on random dates.
        start_date = date(1983, 1, 1).toordinal()
        end_date = date.today().toordinal()
        authors = Author.objects.all()
        # Now generate the data for books.
        for publisher in Publisher.objects.all():
            # Each publisher will get 2 books.
            for book_index in range(1, 3):
                title = self.rand_join(" ",
                                  ["Rearing", "Cooking", "Observing", "Identifying", "Petting"],
                                  ["Birds", "Dogs", "Cats", "Snails", "Lizards"])
                isbn = ''.join(random.choice(string.ascii_uppercase + string.digits)
                               for x in range(0, 13))
                publication_date = date.fromordinal(random.randint(start_date, end_date))
                book = Book(title=title, isbn=isbn, publisher=publisher,
                            publication_date=publication_date)
                book.save()
                # Now associate the book with a number of authors.
                for x in range(0, random.randint(1, 3)):
                    author = authors[random.randint(0, len(authors)-1)]
                    book.authors.add(author)


    def init_librarybranch(self):
        for x in range(0, 5):
            name = self.rand_join(" ",
                                  ["New York", "Texas", "Vermont", "Hawaii"],
                                  ["Municipal", "City", "Public", "Main"],
                                  ["Library"])
            address = self.rand_join(" ",
                                     ["131", "145", "802", "213", "340"],
                                     ["Paso", "Atlantic", "El Segundo", "Priarie"],
                                     ["Drive", "Avenue", "Parkway", "Place", "Lane"])
            library_branch = LibraryBranch(name=name, address=address)
            library_branch.save()

    def init_reader(self):
        # Let's start with just 10 readers.
        for x in range(0, 10):
            username = ''.join(random.choice(string.ascii_uppercase + string.digits)
                           for x in range(0, 13))
            email = self.rand_join("@",
                                   ["gummy", "ham", "justin", "ugly", "narwal"],
                                   ["gmail.com", "yahoo.com", "aol.com", "geocities.net"])
            first_name = random.choice(["Bill", "Jake", "Finn", "Peter", "Shriram"])
            last_name = random.choice(["Macher", "Price", "Cooper", "Nader"])
            user = User(username=username, email=email, first_name=first_name, last_name=last_name)
            user.save()
            address = self.rand_join(' ',
                                     ["222", "333", "444", "555", "666"],
                                     ["Leeman Russ", "Sentinel", "Ogryn", "Kasrkin"],
                                     ["Drive", "Avenue", "Parkway", "Place", "Lane"])
            phone_number = self.rand_join('-',
                                          ['525', '915', '420', '670', '120', '555'],
                                          ['5555', '1234', '6513', '8423', '0932'])
            reader = Reader(user=user, address=address, phone_number=phone_number)
            reader.save()

    def init_bookcopy(self):
        """
        Create a random number of copies of each book for each branch.
        """
        for library_branch in LibraryBranch.objects.all():
            for book in Book.objects.all():
                for copy_number in range(0, random.randint(1, 3)):
                    position = ''.join(random.choice(string.ascii_uppercase + string.digits)
                                       for x in range(0, 6))
                    bookcopy = BookCopy(book=book, library_branch=library_branch,
                                        copy_number=copy_number, position=position)
                    bookcopy.save()

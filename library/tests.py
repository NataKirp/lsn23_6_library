from django.test import TestCase

from .models import Author, Book


class ModelTests(TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            first_name="Александр", last_name="Пушкин", birth_date="1799-06-06"
        )

        self.book = Book.objects.create(
            title="Евгений Онегин", publication_date="1833-01-01", author=self.author
        )

    def test_author_str(self):
        """Тест строкового представления автора."""
        self.assertEqual(str(self.author), "Александр Пушкин")

    def test_book_str(self):
        """Тест строкового представления книги."""
        self.assertEqual(str(self.book), "Евгений Онегин")

    def test_book_author_relationship(self):
        """Тест связи книги с автором."""
        self.assertEqual(self.book.author, self.author)
        self.assertEqual(self.author.books.first(), self.book)

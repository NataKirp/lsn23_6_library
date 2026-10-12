from django.urls import path

from .views import (AuthorCreateView, AuthorListView, AuthorUpdateView,
                    BookCreateView, BookDeleteView, BookDetailView,
                    BooksListView, BookUpdateView, RecommendBookView,
                    ReviewBookView)

app_name = "library"

urlpatterns = [
    path("authors/", AuthorListView.as_view(), name="authors_list"),
    path("author/new/", AuthorCreateView.as_view(), name="author_create"),
    path("author/update/<int:pk>/", AuthorUpdateView.as_view(), name="author_update"),
    path("books/", BooksListView.as_view(), name="books_list"),
    path("books/new/", BookCreateView.as_view(), name="book_create"),
    path("books/<int:pk>/", BookDetailView.as_view(), name="book_detail"),
    path("books/update/<int:pk>/", BookUpdateView.as_view(), name="book_update"),
    path("books/delete/<int:pk>/", BookDeleteView.as_view(), name="book_delete"),
    path(
        "books/recommend/<int:pk>/", RecommendBookView.as_view(), name="book_recommend"
    ),
    path("books/review/<int:pk>/", ReviewBookView.as_view(), name="book_review"),
]

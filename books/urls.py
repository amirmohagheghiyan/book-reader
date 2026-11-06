from django.urls import path

from .views import BookCreateView, BookDeleteView, BookListView, BookUpdateView

app_name = "books"

urlpatterns = [
    path("", BookListView.as_view(), name="list"),
    path("books/new/", BookCreateView.as_view(), name="create"),
    path("books/<int:pk>/edit/", BookUpdateView.as_view(), name="update"),
    path("books/<int:pk>/delete/", BookDeleteView.as_view(), name="delete"),
]

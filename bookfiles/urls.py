from django.urls import path

from .views import BookFileDeleteView, BookFileListView

app_name = "bookfiles"

urlpatterns = [
    path("books/<int:pk>/files/", BookFileListView.as_view(), name="list"),
    path(
        "books/<int:book_pk>/files/<int:pk>/delete/",
        BookFileDeleteView.as_view(),
        name="delete",
    ),
]

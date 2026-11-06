from django.urls import path

from . import views

app_name = "jozveh"

urlpatterns = [
    path("books/<int:pk>/jozveh/", views.JozvehEditorView.as_view(), name="editor"),
    path("books/<int:pk>/jozveh/print/", views.JozvehPrintView.as_view(), name="print"),
    path("books/<int:pk>/jozveh/add/", views.BlockKindPickView.as_view(), name="pick"),
    path("books/<int:pk>/jozveh/add/<str:kind>/", views.BlockCreateView.as_view(), name="add"),
    path(
        "books/<int:pk>/jozveh/blocks/<int:block_pk>/edit/",
        views.BlockUpdateView.as_view(),
        name="edit",
    ),
    path(
        "books/<int:pk>/jozveh/blocks/<int:block_pk>/move/",
        views.BlockMoveView.as_view(),
        name="move",
    ),
    path(
        "books/<int:pk>/jozveh/blocks/<int:block_pk>/delete/",
        views.BlockDeleteView.as_view(),
        name="delete",
    ),
]

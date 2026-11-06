from django.urls import path

from .views import DesignSystemView

app_name = "core"

urlpatterns = [
    path("design-system/", DesignSystemView.as_view(), name="design_system"),
]

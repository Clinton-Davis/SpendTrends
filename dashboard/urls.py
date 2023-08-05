from django.urls import path

from dashboard.views import dashView


urlpatterns = [
    path("", dashView, name="dashView"),
]

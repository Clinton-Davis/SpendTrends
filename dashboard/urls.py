from django.urls import path
from dashboard.views import dashView, UploadView

urlpatterns = [
    path("", dashView, name="dashView"),
    path("upload/", UploadView.as_view(), name="upload_view"),
]

from django.views import View
from django.shortcuts import render


def dashView(request):
    return render(request, "dashboards/index.html", {})


class UploadView(View):
    def post(self, request, *args, **kwargs):
        context = {}
        return render(request, "dashboards/upload.html", context)

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, "dashboards/upload.html", context)

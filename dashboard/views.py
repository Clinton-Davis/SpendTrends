from django.shortcuts import render


def dashView(request):
    return render(request, "dashboards/index.html", {})

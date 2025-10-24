from django.shortcuts import render


def home(request):
    return render(request, 'whichfilm_platform/home.html')

from django.http import HttpResponse
from django.shortcuts import render

def home_page_view(request):
    if request.user.is_authenticated:
        return HttpResponse("<h1>Welcome, you are logged in!</h1>")
    else:
        return HttpResponse("<h1>Hello World</h1>")
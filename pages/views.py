from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view()
def home_page_view(request):
    if request.user.is_authenticated:
        return Response("<h1>Welcome, you are logged in!</h1>")
    else:
        return Response("<h1>Hello World</h1>")
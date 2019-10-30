from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


def board(request):
    return render(request, 'halma/board.html')


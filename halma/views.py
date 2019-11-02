from django.shortcuts import render
from halma.serializers import StateSerializer
from rest_framework import generics
# Create your views here.
from django.http import HttpResponse
from halma.models import State, Action


class StateList(generics.ListCreateAPIView):
    queryset = State.objects.all()
    serializer_class = StateSerializer
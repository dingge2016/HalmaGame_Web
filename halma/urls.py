from django.urls import path

from . import views

urlpatterns = [
    path('', views.board, name='board'),
    path('api/halma', views.StateList.as_view())
]
from django.urls import path

from . import views

urlpatterns = [
    path('api/halma/', views.StateList.as_view())
]
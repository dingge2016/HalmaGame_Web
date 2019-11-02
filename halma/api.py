from halma.models import State
from rest_framework import viewsets, permissions
from .serializers import StateSerializer


class HalmaViewSet(viewsets.ModelViewSet):
    queryset = State.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = StateSerializer

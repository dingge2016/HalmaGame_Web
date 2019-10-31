from django.db import models


# Create your models here.
class State(models.Model):
    state = models.TextField(null=True)


class Action(models.Model):
    action = models.TextField(null=True)

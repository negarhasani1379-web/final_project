from django.db import models

from core.models import BaseModel


class School(BaseModel):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name



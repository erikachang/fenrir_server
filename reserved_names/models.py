from django.db import models


class ReservedName(models.Model):
    name = models.CharField(max_length=24, unique=True)

    class Meta:
        db_table = 'reserved_names'

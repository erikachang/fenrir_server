from django.db import models
from users.models import Friendship
from datetime import datetime


# Create your models here.
class Howl(models.Model):

    friendship = models.OneToOneField(Friendship)
    latitude = models.DecimalField(decimal_places=6, max_digits=8)
    longitude = models.DecimalField(decimal_places=6, max_digits=9)
    description = models.CharField(max_length=60)
    updated_on = models.DateTimeField()
    updates = models.IntegerField(default=0, null=True)

    def info(self):
        data = {
            'howl': {
                'latitude': self.latitude,
                'longitude': self.longitude,
                'description': self.description,
                'updated_on': self.updated_on,
            }
        }
        return data

    def save(self, *args, **kwargs):
        self.updated_on = datetime.now()
        self.updates += 1
        super(Howl, self).save(*args, **kwargs)

    class Meta:
        db_table = 'howls'

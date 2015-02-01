from django.core.management.base import BaseCommand
from django.db import IntegrityError
from reserved_names.models import ReservedName


class Command(BaseCommand):
    help = 'Collects feedback from APNS.'

    def handle(self, *args, **options):
        for name in args:
            try:
                ReservedName.objects.create(name=name)
            except IntegrityError:
                pass
            except:
                raise

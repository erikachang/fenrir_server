from django.core.management.base import BaseCommand
from users.models import Profile
from volky.connection import APNSFeedbackConnection

import logging

logger = logging.getLogger('volky')


class Command(BaseCommand):
    help = 'Collects feedback from APNS.'

    def handle(self, *args, **options):
        logger.debug('starting feedback connection')
        apns = APNSFeedbackConnection()
        apns.connect()

        for feedback in apns.read():
            token, fail_time = feedback
            logger.debug('feedback entry: %s at %s', token, str(fail_time))
            profile = Profile.objects.filter(device_token=token).first()
            print 'feedback entry: %s at %s' % (token, str(fail_time))
            if profile is not None:
                if fail_time > profile.updated_on:
                    profile.device_token = None
                    profile.save()
        apns.disconnect()

from datetime import datetime


class Aps(object):

    def __init__(self, username, description, latitude, longitude,
                 sound='howl.wav', h_type='HOWL'):
        self.username = username
        self.description = description
        self.latitude = latitude
        self.longitude = longitude
        self.sound = sound
        self.h_type = h_type
        self.sent_on = str(datetime.now())

    def dict(self):
        aps = {
            'aps': {
                'alert': {
                    'loc-key': self.h_type,
                    'loc-args': [self.username, self.description],
                },
                'sound': self.sound,
                'content-available': 1,
                'category': 'ACTIONABLE',
                'badge': 1
            },
            'latitude': self.latitude,
            'longitude': self.longitude,
            'sent_on': self.sent_on,
        }

        return aps

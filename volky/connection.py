from django.conf import settings
from socket import socket, AF_INET, SOCK_STREAM
from struct import pack, unpack
from select import select
from ssl import PROTOCOL_TLSv1, wrap_socket
from threading import Thread
from datetime import datetime
from binascii import b2a_hex
import json
import logging
import time
import sys
import traceback

logger = logging.getLogger('volky')

APNS_FEEDBACK_FORMAT = '!IH32s'
APNS_ERROR_FORMAT = '!BBI'
APNS_PACK_FORMAT = '!BH32sBH%ds'
APNS_ENHANCED_FORMAT = '!BH32sBH%dsBHIBHIBHB'
APNS_FRAME_FORMAT = '!BI%ds'

ID_TOKEN = 1
ID_DATA = 2
ID_APSID = 3
ID_EXPIRATION = 4
ID_PRIORITY = 5

TOKEN_LENGTH = 32
APSID_LENGTH = 4
EXP_LENGTH = 4
PRIORITY_LENGTH = 1

NORMAL_PRIORITY = 5
TOP_PRIORITY = 10


class APNSConnection(object):

    _ssl_socket = None

    def __init__(self):
        self.certificate = settings.APNS['CERTIFICATE']
        self.environment = settings.APNS['ENVIRONMENT']
        self.timeout = 0

    def connect(self):
        logger.debug('Starting new connection with APNS')
        s = socket(AF_INET, SOCK_STREAM)
        self._ssl_socket = wrap_socket(s,
                                       certfile=self.certificate,
                                       ssl_version=PROTOCOL_TLSv1)

        try:
            self._ssl_socket.connect(self.endpoint)
            self._ssl_socket.settimeout(self.timeout)
            self.is_connected = True
            logger.debug('Connected to %s environment.', self.environment)
        except:
            logger.debug('Error connecting. Traceback: %s' %
                         (traceback.print_exc()))

    def disconnect(self):
        logger.debug('Disconnecting from %s environment.', self.environment)
        if self._ssl_socket:
            try:
                self._ssl_socket.close()
                self.is_connected = False
            except:
                logger.debug('unexpected error: %s', (sys.exc_info()[0]))

        logger.debug('Disconnected from %s environment.', self.environment)

    def reconnect(self):
        self.disconnect()
        self.connect()


class APNSGatewayConnection(APNSConnection):

    _panic = False
    _watching = False
    _disconnect_signal = False

    def _error_catcher(self):
        logger.debug('watcher started successfully')
        while True:
            if self._disconnect_signal:
                logger.debug('watcher disconnect signal detected')
                break

            if self._ssl_socket:
                self._watching = True
                rlist, _, _ = select([self._ssl_socket], [], [], 2)
                if rlist:
                    data = self._ssl_socket.recv(6)
                    if len(data) > 0:
                        _, err_code, idx = unpack(APNS_ERROR_FORMAT, data)
                        logger.debug(
                            'Received error %d from Apple. Identifier: %d' %
                            (err_code, idx)
                        )
                        self._panic = True

                        if err_code == 10:
                            self._erase_up_to_idx = idx
                        else:
                            self._erase_up_to_idx = idx+1
                        break
        self._watching = False

    def __init__(self):
        super(APNSGatewayConnection, self).__init__()
        self.endpoint = settings.APNS['GATEWAY']
        # if self.environment == 'production':
        #     self.endpoint = ('gateway.push.apple.com', 2195)
        # elif self.environment == 'sandbox':
        #     self.endpoint = ('gateway.sandbox.push.apple.com', 2195)

        self._sent_notifications = []

    def connect(self):
        super(APNSGatewayConnection, self).connect()

        logger.debug('starting watcher')
        self.watcher = Thread(target=self._error_catcher)
        self.watcher.start()
        for x in xrange(1, 3):
            if self._watching:
                break
            time.sleep(1)
        if not self._watching:
            logger.debug('failed to start watcher within 3 secs.')
            return False

        self._panic = False
        return True

    def disconnect(self):
        if self.watcher.is_alive():
            logger.debug('shutting down watcher')
            self._disconnect_signal = True
            self.watcher.join()
            logger.debug('watcher shut down')
        super(APNSGatewayConnection, self).disconnect()

    def reconnect(self):
        self.disconnect()
        return self.connect()

    def send(self, notification):
        if self._panic:
            logger.debug('panic mode is on, unable to send.')
            return False

        token, aps = notification
        aps_data = self._encode(token, aps)

        try:
            count = self._ssl_socket.sendall(aps_data)
            logger.debug('sent %d with %d bytes',
                         len(self._sent_notifications),
                         count)
        except:
            logger.debug('Error %s when sending APS to: %s' %
                         (sys.exc_info()[0], token))

        self._sent_notifications.append((token, aps))
        return True

    def recover_notifications(self):
        del self._sent_notifications[0:self._erase_up_to_idx]
        return self._sent_notifications

    def _encode(self, token, aps):
        data = json.dumps(aps)
        device_token = token.replace(' ', '')
        byte_token = device_token.decode('hex')
        pack_format = APNS_ENHANCED_FORMAT % len(data)
        pack_data = pack(
            pack_format,
            ID_TOKEN, TOKEN_LENGTH, byte_token,
            ID_DATA, len(data), data,
            ID_APSID, APSID_LENGTH, len(self._sent_notifications),
            ID_EXPIRATION, EXP_LENGTH, 0,
            ID_PRIORITY, PRIORITY_LENGTH, TOP_PRIORITY)

        frame_format = APNS_FRAME_FORMAT % len(pack_data)
        frame_data = pack(frame_format, 2, len(pack_data), pack_data)

        return frame_data


class APNSFeedbackConnection(APNSConnection):
    def __init__(self):
        super(APNSFeedbackConnection, self).__init__()
        self.timeout = None
        self.endpoint = settings.APNS['FEEDBACK']

    def _blocks(self):
        BUF_SIZE = 4096
        while True:
            data = self._ssl_socket.recv(BUF_SIZE)
            yield data
            if not data:
                break

    def read(self):
        buff = ''
        for block in self._blocks():
            buff += block

            if not buff:
                logger.debug('buffer is empty. Exiting...')
                break

            if len(buff) < 6:
                logger.debug('not enough data to work with. Exiting...')
                break

            while len(buff) > 6:
                tok_length = unpack('!H', buff[4:6])[0]
                logger.debug('token length is: %d', tok_length)
                tok_range = 6 + tok_length
                if len(buff) > tok_range:
                    fail_time_unix = unpack('!I', buff[0:4])[0]
                    fail_time = datetime.utcfromtimestamp(fail_time_unix)
                    tok = b2a_hex(buff[6:tok_range])

                    yield (tok, fail_time)

                    buff = buff[tok_range:]
                else:
                    break

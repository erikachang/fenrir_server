from Queue import PriorityQueue, Empty
from volky.connection import APNSGatewayConnection
from threading import Thread
from django.conf import settings
import logging
import traceback
import time

logger = logging.getLogger('volky')

RETRY_COUNT = 3


class APNSQueueSystem():

    max_workers = settings.APNS_MAX_WORKERS

    def __init__(self):
        self.workers = 0
        self.main_queue = PriorityQueue()
        logger.debug("starting queue")

    def worker(self):
        self.workers += 1
        apns = APNSGatewayConnection()
        try:
            for x in xrange(0, RETRY_COUNT):
                logger.debug('Connecting... tries: %d', x)
                connected = apns.connect()
                if connected:
                    break

            if not connected:
                logger.debug(
                    'failed to connect to APNS. Is APNS service online?')

            while connected:
                _, notification = self.main_queue.get(block=True, timeout=10)

                successful = apns.send(notification)

                if not successful:
                    logger.debug(
                        'Notification raised an error.' +
                        ' Connection must be restarted.'
                    )
                    unsent_notifications = apns.recover_notifications()

                    if unsent_notifications.count(notification) == 0:
                        unsent_notifications.append(notification)

                    for u in unsent_notifications:
                        self.reenqueue_aps(u)

                    for x in xrange(0, RETRY_COUNT):
                        connected = apns.reconnect()
                        if connected:
                            break

                    if not connected:
                        logger.debug('Failed to reconnect. Worker exiting...')
        except Empty:
            logger.debug('Queue is empty.')
            pass
        except:
            logger.debug(
                'Error sending APS. Traceback: %s' % (traceback.print_exc()))
        finally:
            logger.debug('Worker exiting...')
            self.workers -= 1
            apns.disconnect()

    def enqueue_async(self, tokens, aps):
        for token in tokens:
            self.main_queue.put((2, (token, aps)))
        logger.debug('work enqueued.')

    def enqueue_multiple(self, tokens, aps):
        enqueuer = Thread(target=self.enqueue_async, args=(tokens, aps))
        enqueuer.start()
        self.dispatch_worker()

    def reenqueue_aps(self, notification):
        self.main_queue.put((1, notification))
        logger.debug('work reenqueued.')
        self.dispatch_worker()

    def enqueue_aps(self, token, aps):
        self.main_queue.put((2, (token, aps)))
        logger.debug('work enqueued.')
        self.dispatch_worker()

    def bogus(self, token, aps):
        corr = token
        token = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        self.main_queue.put((2, (token, aps)))
        token = corr
        self.dispatch_worker()

        aps['aps']['alert'] = 'Correct 1'
        self.main_queue.put((2, (token, aps)))
        time.sleep(2)
        aps['aps']['alert'] = 'Correct 2'
        self.main_queue.put((2, (token, aps)))

    def dispatch_worker(self):
        if self.workers < self.max_workers:
            logger.debug('can spawn worker. starting...')
            w = Thread(target=self.worker)
            w.daemon = True
            w.start()
        else:
            logger.debug('worker count has reached maximum.')

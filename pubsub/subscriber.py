#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

from kombu import Exchange, Queue, Connection
from kombu.mixins import ConsumerMixin
from kombu.log import get_logger

logger = get_logger(__name__)


class Worker(ConsumerMixin):

    def __init__(self, config, connection, queues):
        self.config = config
        self.connection = connection
        self.queues = queues

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=self.queues,
                         accept=['json'],
                         callbacks=[self.process_task])]

    def process_task(self, body, message):
        routing_key = message.delivery_info['routing_key']
        logger.info('Recieved event', extra={'routing_key': routing_key, 'message_body': body})
        try:
            self.queue_task(routing_key, body)
        except Exception as e:
            logger.exception('Error while handling message.', extra={'routing_key': routing_key, 'message_body': body})

        message.ack()

    def queue_task(self, routing_key, body):
        """
        Queue task from AMPQ message.

        Args:
            routing_key(str): Routing key message delivered with
            body(dict): Body of message.

        Raises:
            ValueError: if body is not a dictionary.
            KeyError: if body does not contain the required keys.

        """
        if not isinstance(body, dict):
            raise ValueError('Body must be a dictionary.')

        celery_app = self._get_celery_app()

        task_mappings = self.config.task_mapping

        for task_mapping in task_mappings:

            if not self.does_routing_key_match(routing_key, task_mapping['routing_key']):
                continue

            task_name = task_mapping['task']
            get_args = task_mapping['get_args']
            should_schedule = task_mapping['should_schedule']
            get_celery_kwargs = task_mapping.get('celery_kwargs', None)

            will_schedule = should_schedule(routing_key, body)

            if not will_schedule:
                logger.info('Will schedule is False, no task scheduled.')
                continue

            task_args, task_kwargs = get_args(routing_key, body)
            celery_kwargs = get_celery_kwargs(routing_key, body) if get_celery_kwargs else {}
            task_result = celery_app.send_task(task_name, args=task_args, kwargs=task_kwargs, **celery_kwargs)

            logger.info('Task queued', extra={'task_id': task_result.id, 'task_name': task_name})

    def _get_celery_app(self):
        """Uses the method defined in the config to fetch the celery app"""
        get_app = self.config.get_celery_app
        return get_app()

    @staticmethod
    def does_routing_key_match(test_string, routing_key):
        """
        Does some test string match a routing key.

        Args:
            test_string(str)
            routing_key(str)

        Return:
            bool: Do they match.

        """

        def convert(string):
            if string == '*':
                return r'\w+'
            if string == '#':
                return r'(\w+)(\.\w+)*'
            return string

        routing_key_els = routing_key.split('.')
        routing_key_els_regex = '\.'.join([convert(i) for i in routing_key_els])
        return re.match(routing_key_els_regex, test_string) is not None


class Subscriber(object):

    def __init__(self, config):
        self.config = config

    def start(self):
        """
        Start subscriber.

        """

        with Connection(self.config.broker_url) as conn:
            data_pipeline_exchange = Exchange(self.config.exchange, 'topic')

            queue = Queue(self.config.queue_name)
            queue.maybe_bind(conn)
            queue.declare()

            for routing_key in set([i['routing_key'] for i in self.config.task_mapping]):
                queue.bind_to(data_pipeline_exchange, routing_key)

            worker = Worker(self.config, conn, [queue])

            logger.info('Starting subscriber...')
            worker.run()

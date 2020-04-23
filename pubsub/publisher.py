#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from kombu import Connection, Exchange
from kombu.pools import producers


class Publisher(object):
    """
    Publisher.

    Args:
        config(PubSubConfig): Configuration to use.

    """

    def __init__(self, config):
        self.config = config

    def publish_event(self, routing_key, body):
        """
        Publish event to pubsub rabbitmq.

        Args:
            routing_key(str): Routing key.
            body(dict): Body of message

        """
        with Connection(self.config.broker_url) as connection:
            data_pipeline_exchange = Exchange(self.config.exchange, 'topic')

            with producers[connection].acquire(block=True) as producer:
                producer.publish(
                    body=body,
                    routing_key=routing_key,
                    exchange=data_pipeline_exchange,
                    declare=[data_pipeline_exchange],
                    retry=True,
                    retry_policy={"max_retries": 3, "interval_start": 0, "interval_step": 0.5, "interval_max": 1}
                )

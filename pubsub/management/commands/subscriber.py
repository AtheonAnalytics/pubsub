#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings

from pubsub import PubSubConfig
from pubsub.subscriber import Subscriber


class Command(BaseCommand):
    help = 'Start Subscriber'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting subscriber...')
        config = PubSubConfig.from_object(settings)
        Subscriber(config).start()

#!/usr/bin/python
# -*- coding: utf-8 -*-


class MisconfigurationException(Exception):
    pass


class PubSubConfig(object):
    """
    Configuration object.

    Args:
        task_mapping(list): Maps messages to tasks. For example:
            [
                    {
                        'routing_key': 'etl.*.*.*'
                        'task': query.tasks.execute_script,
                        'get_args': lambda routing_key, body : ([], {})
                        'should_schedule': lambda routing_key, body : True
                        'celery_kwargs': {'countdown': 5}
                    },
            ]
        get_celery_app(function): Must return celery app instance.
        broker_url(str): Rabbitmq url, including credentials.
        exchange(str): Rabbitmq exchange to connect to.
        queue_name(str): Rabbitmq queue name for subscriber

    """

    def __init__(self, task_mapping, get_celery_app, broker_url, exchange, queue_name):
        self.task_mapping = task_mapping
        self.get_celery_app = get_celery_app
        self.broker_url = broker_url
        self.exchange = exchange
        self.queue_name = queue_name

    @classmethod
    def from_object(cls, obj, prefix="PUBSUB_"):
        """
        Return configuration instance from an object.

        Notes:
            Variables should be in uppercase.

        Args:
            obj: object to configure from.
            prefix(optional[str]): Prefix when retrieving settings.

        Examples:
            You could use this to configure from django settings::

                from django.conf import settings
                config = PubSubConfig.from_object(settings)

        Returns:
            PubSubConfig instance.

        """
        args = [
            "task_mapping",
            "get_celery_app",
            "broker_url",
            "exchange",
            "queue_name",
        ]
        arg_names = ["{}{}".format(prefix, name).upper() for name in args]
        arg_dict = {}

        for arg_name, prefix_arg_name in zip(args, arg_names):
            # Flask config is dict type
            if isinstance(obj, dict):
                arg_val = obj.get(prefix_arg_name)
            else:
                arg_val = getattr(obj, prefix_arg_name, None)

            arg_dict[arg_name] = arg_val

            if arg_val is None:
                raise MisconfigurationException(
                    "Missing configuration: {}".format(arg_name)
                )

        return cls(**arg_dict)

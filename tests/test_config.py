from dataclasses import dataclass
from typing import Callable

import pytest

from pubsub.config import PubSubConfig, MisconfigurationException


def test_config_init():
    config = PubSubConfig(
        task_mapping=[],
        get_celery_app=lambda x: x,
        broker_url="memory://",
        exchange="test_exchange",
        queue_name="test_queue",
    )
    assert config.task_mapping == []
    assert config.broker_url == "memory://"
    assert config.exchange == "test_exchange"
    assert config.queue_name == "test_queue"


def test_config_init_from_obj_dict():
    config = PubSubConfig.from_object(
        dict(
            PUBSUB_TASK_MAPPING=[],
            PUBSUB_GET_CELERY_APP=lambda x: x,
            PUBSUB_BROKER_URL="memory://",
            PUBSUB_EXCHANGE="test_exchange",
            PUBSUB_QUEUE_NAME="test_queue",
        )
    )
    assert config.task_mapping == []
    assert config.broker_url == "memory://"
    assert config.exchange == "test_exchange"
    assert config.queue_name == "test_queue"


def test_config_init_from_obj():
    @dataclass()
    class Configuration:
        PUBSUB_TASK_MAPPING: list
        PUBSUB_GET_CELERY_APP: Callable
        PUBSUB_BROKER_URL: str
        PUBSUB_EXCHANGE: str
        PUBSUB_QUEUE_NAME: str

    config = PubSubConfig.from_object(
        Configuration(
            PUBSUB_TASK_MAPPING=[],
            PUBSUB_GET_CELERY_APP=lambda x: x,
            PUBSUB_BROKER_URL="memory://",
            PUBSUB_EXCHANGE="test_exchange",
            PUBSUB_QUEUE_NAME="test_queue",
        )
    )
    assert config.task_mapping == []
    assert config.broker_url == "memory://"
    assert config.exchange == "test_exchange"
    assert config.queue_name == "test_queue"


def test_config_init_from_obj_misconfiguration():
    with pytest.raises(MisconfigurationException):
        PubSubConfig.from_object(
            dict(
                PUBSUB_TASK_MAPPING=[],
                PUBSUB_GET_CELERY_APP=lambda x: x,
                PUBSUB_BROKER_URL="memory://",
                PUBSUB_EXCHANGE="test_exchange",
            )
        )

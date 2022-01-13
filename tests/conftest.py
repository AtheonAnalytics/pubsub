import logging

import pytest
from flask import Flask

from pubsub.config import PubSubConfig
from pubsub.flask.commands import subscriber

pytest_plugins = ("celery.contrib.pytest",)


@pytest.fixture()
def ps_config():
    return PubSubConfig(
        task_mapping=[
            dict(
                task="test_task",
                get_args=lambda x, y: ((1,), {1: 2}),
                should_schedule=lambda x, y: True,
                routing_key="test.routing_key",
            )
        ],
        get_celery_app=lambda x: x,
        broker_url="memory://",
        exchange="test_exchange",
        queue_name="test_queue",
    )


def create_app(config_object):
    app = Flask(__name__.split(".")[0])
    app.config.from_object(config_object)
    app.cli.add_command(subscriber)
    return app


@pytest.fixture
def app():
    """Create application for the tests."""
    _app = create_app("tests.settings")
    _app.logger.setLevel(logging.CRITICAL)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()

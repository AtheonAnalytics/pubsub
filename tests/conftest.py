import pytest

from pubsub.config import PubSubConfig


@pytest.fixture()
def ps_config():
    return PubSubConfig(
        task_mapping=[
            dict(
                task="test_task",
                get_args=lambda x, y: ((1,), {1: 2}),
                should_schedule=lambda x, y: True,
                routing_key="test.routing_key"
            )
        ],
        get_celery_app=lambda x: x,
        broker_url="memory://",
        exchange="test_exchange",
        queue_name="test_queue",
    )

from unittest.mock import patch, MagicMock

from kombu import Connection, Exchange, Queue

from pubsub.subscriber import Subscriber, Worker
from pubsub.publisher import Publisher


def test_subscriber_starts(ps_config):
    subscriber = Subscriber(config=ps_config)
    publisher = Publisher(config=ps_config)
    publisher.publish_event("test_routing_key", dict(some_key="some_value"))

    with patch("pubsub.subscriber.Worker.run") as worker_mock:
        subscriber.start()
        worker_mock.assert_called_once()


def test_worker_consumption():
    routing_key = "test.routing_key"
    message_body = {"test_key_1": "test_value_1", "test_key_2": 123456}
    test_exchange = Exchange("test_exchange", "topic")
    test_queue = Queue("test_queue", exchange=test_exchange, routing_key=routing_key)

    with Connection("memory://") as conn:
        producer = conn.Producer(serializer="json")
        producer.publish(
            message_body,
            exchange=test_exchange,
            routing_key=routing_key,
            declare=[test_queue],
        )

        with patch("pubsub.subscriber.Worker.queue_task") as task_mock:
            worker = Worker(dict(), conn, [test_queue])
            for _ in worker.consume():
                break

            task_mock.assert_called_once_with(routing_key, message_body)


def test_task_queueing_called(ps_config):
    with patch("pubsub.subscriber.Worker._get_celery_app") as celery_mock:
        worker = Worker(ps_config, None, None)
        worker.queue_task("test.routing_key", dict(test_key="test_value"))
        celery_mock.return_value.send_task.assert_called_once_with(
            "test_task", args=(1,), kwargs={1: 2}
        )


def test_task_queueing_not_called(ps_config):
    with patch("pubsub.subscriber.Worker._get_celery_app") as celery_mock:
        worker = Worker(ps_config, None, None)
        worker.queue_task("test.unrecognised_routing_key", dict(test_key="test_value"))
        celery_mock.return_value.send_task.assert_not_called()


def test_task_queueing_with_celery(celery_app, celery_worker, ps_config):
    test_func = MagicMock()

    @celery_app.task(name="test_task")
    def test_task(*args, **kwargs):
        test_func()
        return True

    celery_worker.reload()

    with patch("pubsub.subscriber.Worker._get_celery_app", return_value=celery_app):
        worker = Worker(ps_config, None, None)
        results = worker.queue_task("test.routing_key", dict(test_key="test_value"))
        results[0].get()
        test_func.assert_called_once()


def test_routing_keys_match():
    assert Worker.does_routing_key_match("test.this.key", "test.this.key") is True
    assert Worker.does_routing_key_match("test.this.key", "test.this.keys") is False
    assert Worker.does_routing_key_match("test.this.key", "tests.this.key") is False
    assert Worker.does_routing_key_match("test.this.key_extra", "test.this.key") is False

    assert Worker.does_routing_key_match("test.this.key", "test.*.key") is True
    assert Worker.does_routing_key_match("test.that.key", "test.*.key") is True
    assert Worker.does_routing_key_match("test.this.this.key", "test.*.key") is False

    assert Worker.does_routing_key_match("test.this.key", "test.#.key") is True
    assert Worker.does_routing_key_match("test.this.that.key", "test.#.key") is True
    assert Worker.does_routing_key_match("test.this.keys", "test.#.key") is False

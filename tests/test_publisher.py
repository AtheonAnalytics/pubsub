from unittest.mock import patch

from kombu import Exchange

from pubsub.publisher import Publisher


def test_publish_event(ps_config):
    publisher = Publisher(config=ps_config)

    with patch('pubsub.publisher.producers') as publish_mock:
        publisher.publish_event("test_routing_key", dict(some_key="some_value"))

        publish_mock.__getitem__().acquire().__enter__().publish.assert_called_with(
            body={"some_key": "some_value"},
            routing_key="test_routing_key",
            exchange=Exchange("test_exchange", "topic"),
            declare=[Exchange("test_exchange", "topic")],
            retry=True,
            retry_policy={
                "max_retries": 3,
                "interval_start": 0,
                "interval_step": 0.5,
                "interval_max": 1,
            },
        )

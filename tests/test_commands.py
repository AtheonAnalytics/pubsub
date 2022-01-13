from unittest.mock import patch

from pubsub.flask.commands import subscriber


def test_flask_command(app):
    with patch("pubsub.flask.commands.Subscriber.start") as sub_mock:
        runner = app.test_cli_runner()
        result = runner.invoke(subscriber)
        assert "Starting subscriber..." in result.output
        sub_mock.assert_called_once()

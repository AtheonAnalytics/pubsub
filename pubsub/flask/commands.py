import click
from flask import current_app
from flask.cli import with_appcontext

from pubsub import PubSubConfig, Subscriber


@click.command()
@with_appcontext
def subscriber():
    """Start Subscriber"""
    click.echo("Starting subscriber...")
    config = PubSubConfig.from_object(current_app.config)
    Subscriber(config).start()

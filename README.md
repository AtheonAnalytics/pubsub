[![codecov](https://codecov.io/gh/AtheonAnalytics/pubsub/branch/master/graph/badge.svg?token=MJM8ZZJEOY)](https://codecov.io/gh/AtheonAnalytics/pubsub)
![example workflow](https://github.com/AtheonAnalytics/pubsub/actions/workflows/tests.yaml/badge.svg)
![example workflow](https://github.com/AtheonAnalytics/pubsub/actions/workflows/linting.yml/badge.svg)


<h2 align="center">PubSub</h2>

Pubsub is a messaging library for Python that helps facilitate comminication between microservices.
As the name would suggest, Pubsub serves two main purposes; publishing messages to a broker and subscribing to 
a broker in order to receive published messages from it. Messages that are received from the broker are automatically 
passed to Celery, to be run as tasks.

Configuration for Pubsub can be supplied as either a dictionary or class object. This means that it can be easily integrated with Flask and 
Django apps, using their respective settings files.

---
### Getting Started

Pubsub is hosted on the Atheon [CloudRepo](https://www.cloudrepo.io/) site and can be added to a project using pip or 
dependency management tools (such as Poetry)

### Configuration

In the Python application that you wish to use Pubsub, you will need to define some configuration. The variables that will 
need to be defined are:

<dl>
    <dt>PUBSUB_BROKER_URL</dt>
    <dd>URL of the broker that messages will be sent to/received from</dd>
    <dt>PUBSUB_EXCHANGE</dt>
    <dd>Name of the exchange</dd>
</dl>

If you only wish to publish messages, then these are the only variables that need to be defined. If however, you also wish to subscribe, there are a few more than you will need to define: 

<dl>
    <dt>PUBSUB_GET_CELERY_APP</dt>
    <dd>Method that can be called to return the Celery app</dd>
</dl>
eg:

```python
def get_celery_app():
    from my_app.celery import app
    return app
```

<dl>
    <dt>PUBSUB_QUEUE_NAME</dt>
    <dd>Name of the queue</dd>
    <dt>PUBSUB_TASK_MAPPING</dt>
    <dd>List of mappings between the routing key used when publishing to the broker and the task that should be run when the subscriber 
receives the message. Mandatory keys for the items in this list are 'routing_key', 'task', 'should_schedule' and 'get_args'. 
'celery_kwargs' is an optional key.</dd>
</dl>

eg:
```python
PUBSUB_TASK_MAPPING = [
    {
        'routing_key': 'app1.matches.published',
        'task': 'query.tasks.execute_script',
        'should_schedule': lambda routing_key, body: True,
        'get_args': lambda routing_key, body: (
            [],
            dict()
        ),
        'celery_kwargs': lambda routing, body: {
            'countdown': 10,
        },
    },
    {
        'routing_key': 'app2.exclusions.published',
        'task': 'query.tasks.execute_script',
        'should_schedule': lambda routing_key, body: True,
        'get_args': lambda routing_key, body: (
            [],
            dict()
        ),
    }
]
```
### Usage

To use the publisher, you can simply load your configuration, pass it to the publisher and then call 
publish_event with a routing key and message body

Flask example:
```python
from pubsub.config import PubSubConfig
from pubsub.publisher import Publisher
from flask import current_app

config = PubSubConfig.from_object(current_app.config)
publisher = Publisher(config=config)
publisher.publish_event(routing_key="a_routing_key", body={"foo": "bar"})
```

To use the subscriber, you can follow a similar pattern:
```python
from flask import current_app

from pubsub import PubSubConfig, Subscriber

config = PubSubConfig.from_object(current_app.config)
Subscriber(config=config).start()
```

Alternatively, you can use one of the built-in commands to do this for you:
```python
from pubsub.flask.commands import subscriber

def register_commands(app):
    ...
    app.cli.add_command(subscriber)

    
def create_app(config_object="settings"):
    ...
    register_commands(app)
    return app
```
```shell
sub (){
    exec flask subscriber
}
```
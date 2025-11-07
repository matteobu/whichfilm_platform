"""
WhichMovie Django project initialization.
"""

# Initialize Dramatiq broker and import all tasks when Django starts
default_app_config = 'whichmovie.apps.WhichmovieConfig'


def ready():
    """Initialize Dramatiq and load all tasks."""
    import django_dramatiq
    django_dramatiq.setup()

    # Import all tasks from apps to register them with Dramatiq
    from movies import tasks as movies_tasks  # noqa

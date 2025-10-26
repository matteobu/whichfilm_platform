from django.apps import AppConfig
from django.core.management import call_command
import threading


class IntegrationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "integrations"

    def ready(self):
        """
        Start the APScheduler when Django is ready.
        This runs once when the Django app starts.
        """
        # Run in a separate thread to avoid Django reentrant error
        threading.Thread(target=self._start_scheduler, daemon=True).start()

    @staticmethod
    def _start_scheduler():
        """Start the scheduler in a separate thread"""
        from integrations.tasks import start_scheduler
        start_scheduler()

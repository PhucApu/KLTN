from django.apps import AppConfig
from .utils.VnCoreNLP import load_vncorenlp


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    def ready(self):
        """Chạy khi Django khởi động."""
        # load_vncorenlp()
        
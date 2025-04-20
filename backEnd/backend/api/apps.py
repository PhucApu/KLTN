from django.apps import AppConfig
<<<<<<< Updated upstream
=======
from .utils.VnCoreNLP import load_vncorenlp
>>>>>>> Stashed changes


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"
<<<<<<< Updated upstream
=======

    def ready(self):
        """Chạy khi Django khởi động."""
        # load_vncorenlp()
        
>>>>>>> Stashed changes

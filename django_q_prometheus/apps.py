from django.apps import AppConfig

class DjangoQConfig(AppConfig):
    name = "django_q_prometheus"

    def ready(self):
        """ Inject the signals 
        """
        import django_q_prometheus.signals
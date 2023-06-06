from django.apps import AppConfig


class CapacitacionesConfig(AppConfig):
    name = 'capacitaciones'

    def ready(self):
        from jobs import updater
        updater.start()

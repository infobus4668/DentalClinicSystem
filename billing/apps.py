# DENTALCLINICSYSTEM/billing/apps.py

from django.apps import AppConfig

class BillingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'billing'

    def ready(self):
        """
        This method is run when the app is ready.
        We import our signals here to ensure they are connected.
        """
        import billing.signals # <<<--- ADD THIS LINE
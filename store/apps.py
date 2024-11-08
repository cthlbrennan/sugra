from django.apps import AppConfig


class StoreConfig(AppConfig):
    """
    Django app configuration for the Store application.
    Handles app-specific configuration and initialization, including:
    - Database configuration
    - Signal registration
    - App naming and metadata
    """
    
    # Use BigAutoField as the primary key type for all models
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Internal reference name for the app
    name = 'store'

    def ready(self):
        """
        Performs initialization tasks when the app is ready.
        This method is called by Django once when the application is loading.
        
        Currently:
        - Imports and registers signal handlers from store.signals
        """
        import store.signals  # Import signals to ensure they are registered
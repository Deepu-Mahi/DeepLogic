from django.apps import AppConfig

class SubmitConfig(AppConfig):
    # Specifies the default type of primary key field for models in this app
    default_auto_field = 'django.db.models.BigAutoField'
    
    # The name of the app (should match the folder name)
    name = 'submit'

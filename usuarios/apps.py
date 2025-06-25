from django.apps import AppConfig  # 👈 Esta línea faltaba

class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usuarios'
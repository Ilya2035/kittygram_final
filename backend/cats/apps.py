"""Прописываем приложение."""

from django.apps import AppConfig


class CatsConfig(AppConfig):
    """Класс конфигурации приложения Cats."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cats'

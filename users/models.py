from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # ваши дополнительные поля

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='custom_user_groups',  # ← любое уникальное имя
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='custom_user_permissions',  # ← любое уникальное имя
        help_text='Specific permissions for this user.',
    )
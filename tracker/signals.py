# tracker/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from .models import TrackedProduct
import json

@receiver(post_save, sender=TrackedProduct)
def create_or_update_periodic_task(sender, instance, created, **kwargs):
    if created:
        # Создаём интервал: каждые N минут
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=5,  # ← N минут
            period=IntervalSchedule.MINUTES,
        )

        # Создаём задачу в Celery Beat
        PeriodicTask.objects.create(
            interval=schedule,
            name=f'Update price for product {instance.id}',
            task='tracker.tasks.update_product_price',
            args=json.dumps([instance.id]),
            enabled=True,
        )

@receiver(post_delete, sender=TrackedProduct)
def delete_periodic_task(sender, instance, **kwargs):
    task_name = f'Update price for product {instance.id}'
    PeriodicTask.objects.filter(name=task_name).delete()
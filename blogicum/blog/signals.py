from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Comment, Post  # noqa: F401


@receiver(post_save, sender=Comment)
def update_comment_count_on_create(sender, instance, created, **kwargs):
    """Обновляет количество комментариев при создании нового."""
    if created:
        post = instance.post
        post.comment_count = post.comments.count()
        post.save()


@receiver(post_delete, sender=Comment)
def update_comment_count_on_delete(sender, instance, **kwargs):
    """Обновляет количество комментариев при удалении."""
    post = instance.post
    post.comment_count = post.comments.count()
    post.save()

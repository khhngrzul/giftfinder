from django.conf import settings
from django.db import models
from gifts.models import Gift


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    gift = models.ForeignKey(Gift, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        unique_together = ('user', 'gift')


class SavedGift(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    gift = models.ForeignKey(Gift, on_delete=models.CASCADE, related_name='saves')

    class Meta:
        unique_together = ('user', 'gift')


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    gift = models.ForeignKey(Gift, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:30]
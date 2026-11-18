from django.conf import settings
from django.db import models


class Interest(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Personality(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Occasion(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Gift(models.Model):
    GENDER = [('any', 'Бүгд'), ('male', 'Эрэгтэй'), ('female', 'Эмэгтэй')]
    STATUS = [('pending', 'Хүлээгдэж буй'), ('approved', 'Зөвшөөрсөн'),
              ('rejected', 'Татгалзсан')]

    name = models.CharField(max_length=120)
    description = models.TextField()
    image = models.ImageField(upload_to='gifts/', blank=True, null=True)
    price = models.PositiveIntegerField()
    age_min = models.PositiveSmallIntegerField(default=0)
    age_max = models.PositiveSmallIntegerField(default=99)
    gender = models.CharField(max_length=6, choices=GENDER, default='any')
    interests = models.ManyToManyField(Interest, blank=True)
    personalities = models.ManyToManyField(Personality, blank=True)
    occasions = models.ManyToManyField(Occasion, blank=True)
    buy_url = models.URLField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='pending')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name='gifts')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


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
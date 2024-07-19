from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class AuthToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    qr_id = models.TextField(unique=True)
    name = models.TextField()
    token = models.TextField(blank=True)
    hashed_token = models.TextField()
    active = models.BooleanField(default=True)
    next = models.ForeignKey('self', related_name="+", null=True, blank=True, on_delete=models.CASCADE)
    prev = models.ForeignKey('self', related_name="+", null=True, blank=True, on_delete=models.CASCADE)
    hint = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user} - {self.name}"

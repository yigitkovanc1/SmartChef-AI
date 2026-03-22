from django.db import models
from django.contrib.auth.models import User

class PasswordHistory(models.Model):
    """ Kullanıcının eski şifrelerini (hashlenmiş olarak) tutar """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    password_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] # En yeni şifre en üstte gelsin

class ResetCode(models.Model):
    """ Şifremi unuttum işlemi için 6 haneli kodları tutar """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

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





# ==========================================
# KULLANICI PROFİLİ TABLOSU
# ==========================================
class Profile(models.Model):
    # OneToOneField: Her kullanıcının sadece 1 profili olabilir, her profil 1 kullanıcıya aittir.
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # Kullanıcının kendisini anlattığı kısa biyografi yazısı
    bio = models.TextField(max_length=500, blank=True, null=True)

    # Profil fotoğrafı. Kullanıcı yüklemezse default.png resmini kullanır.
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} Profili"


# ==========================================
# SİNYALLER (OTOMATİK PROFİL OLUŞTURUCU)
# ==========================================
# Sinyal: Bir User (Kullanıcı) veritabanına kaydedildiğinde (post_save) bu fonksiyonu tetikle.
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:  # Eğer kullanıcı YENİ kayıt olduysa...
        Profile.objects.create(user=instance)  # Arka planda hemen bir Profil tablosu yarat ve ona bağla!


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()  # Kullanıcı güncellendiğinde profilini de kaydet.

from django.db.models.signals import post_save
from django.dispatch import receiver

# Kullanıcıların profil fotoğraflarını tutacak tablo
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profil_fotograflari/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} Profili"


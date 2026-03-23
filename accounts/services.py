from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import random
from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password
from .models import PasswordHistory, ResetCode


def create_user_account(kullanici_adi, email, sifre):
    """ Yeni kullanıcı oluşturur ve şifresini otomatik hash'ler. """

    if User.objects.filter(username=kullanici_adi).exists():
        return None, "Bu kullanıcı adı zaten alınmış."
    if User.objects.filter(email=email).exists():
        return None, "Bu e-posta adresi sistemde kayıtlı."


    yeni_kullanici = User.objects.create_user(username=kullanici_adi, email=email, password=sifre)
    return yeni_kullanici, "Kayıt başarıyla tamamlandı!"


def authenticate_user(request, email, sifre):
    """ E-posta ve şifre ile giriş kontrolü yapar """

    user_record = User.objects.filter(email=email).first()


    if user_record:
        user = authenticate(request, username=user_record.username, password=sifre)
        if user is not None:
            return True, user, "Mutfağa hoş geldin!"

    return False, None, "E-posta adresin veya şifren hatalı. Lütfen tekrar dene."
def send_password_reset_code(email):
    """ Kullanıcıyı bulur, 6 haneli kod üretir ve gerçek e-posta atar """
    user = User.objects.filter(email=email).first()
    if not user:
        return False, "Sistemde bu e-posta adresiyle kayıtlı bir şef bulunamadı."


    kod = str(random.randint(100000, 999999))


    ResetCode.objects.filter(user=user).delete()
    ResetCode.objects.create(user=user, code=kod)


    baslik = "SmartChef - Şifre Sıfırlama Kodunuz"
    mesaj = f"Merhaba Şef,\n\nŞifrenizi sıfırlamak için onay kodunuz: {kod}\n\nLütfen bu kodu kimseyle paylaşmayın."
    gonderen = None

    try:
        send_mail(baslik, mesaj, gonderen, [email], fail_silently=False)
        return True, "6 haneli doğrulama kodu e-posta adresinize gönderildi."
    except Exception as e:
        return False, "Mail sunucusuna bağlanılamadı. Ayarlarınızı kontrol edin."

def reset_user_password(email, code, new_password):
    """ Kodu doğrular, mevcut ve eski şifrelerle karşılaştırır, şifreyi değiştirir """
    user = User.objects.filter(email=email).first()
    if not user:
        return False, "Kullanıcı bulunamadı."


    reset_record = ResetCode.objects.filter(user=user, code=code).first()
    if not reset_record:
        return False, "Girdiğiniz 6 haneli kod hatalı veya süresi dolmuş."




    if user.check_password(new_password):
        return False, "Yeni şifreniz şu an kullandığınız mevcut şifrenizle tamamen aynı olamaz!"


    eski_sifreler = PasswordHistory.objects.filter(user=user).order_by('-created_at')[:2]
    for gecmis in eski_sifreler:
        if check_password(new_password, gecmis.password_hash):
            return False, "Güvenlik ihlali! Yeni şifreniz eski şifrelerinizden biriyle aynı olamaz."


    user.set_password(new_password)
    user.save()


    PasswordHistory.objects.create(user=user, password_hash=user.password)


    reset_record.delete()

    return True, "Şifreniz başarıyla güncellendi! Artık giriş yapabilirsiniz."
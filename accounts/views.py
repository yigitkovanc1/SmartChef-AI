from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .services import create_user_account, authenticate_user, send_password_reset_code, reset_user_password
from recipes.models import Recipe, RecipeCostHistory
from .models import Profile
from markets.models import MarketCost
from collections import defaultdict
from recipes.models import Favorite
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from .models import PasswordHistory


def kayit_ol_view(request):
    if request.method == 'POST':
        kullanici_adi = request.POST.get('kullanici_adi')
        email = request.POST.get('email')
        sifre = request.POST.get('sifre')
        sifre_tekrar = request.POST.get('sifre_tekrar')


        if sifre != sifre_tekrar:
            messages.error(request, "Girdiğiniz şifreler birbiriyle eşleşmiyor!")
            return render(request, 'accounts/register.html')

        basarili_mi, mesaj = create_user_account(kullanici_adi, email, sifre)
        if basarili_mi:
            messages.success(request, mesaj)
            return redirect('giris_yap')
        else:
            messages.error(request, mesaj)

    return render(request, 'accounts/register.html')


def giris_yap_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')  # E-posta ile giriş
        sifre = request.POST.get('sifre')

        basarili_mi, user, mesaj = authenticate_user(request, email, sifre)

        if basarili_mi:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, mesaj)

    return render(request, 'accounts/login.html')


def cikis_yap_view(request):
    logout(request)
    return redirect('giris_yap')


@login_required(login_url='giris_yap')
def ana_sayfa_view(request):
    return render(request, 'home.html')


def sifremi_unuttum_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        basarili_mi, mesaj = send_password_reset_code(email)

        if basarili_mi:
            messages.success(request, mesaj)
            request.session['reset_email'] = email
            return redirect('sifre_sifirla')
        else:
            messages.error(request, mesaj)

    return render(request, 'accounts/forgot_password.html')


def sifre_sifirla_view(request):
    email = request.session.get('reset_email')
    if not email:
        messages.error(request, "Lütfen önce e-posta adresinizi girin.")
        return redirect('sifremi_unuttum')

    if request.method == 'POST':
        kod = request.POST.get('kod')
        yeni_sifre = request.POST.get('yeni_sifre')
        yeni_sifre_tekrar = request.POST.get('yeni_sifre_tekrar')


        if yeni_sifre != yeni_sifre_tekrar:
            messages.error(request, "Girdiğiniz yeni şifreler birbiriyle eşleşmiyor! Lütfen tekrar deneyin.")
            return render(request, 'accounts/reset_password.html', {'email': email})

        basarili_mi, mesaj = reset_user_password(email, kod, yeni_sifre)

        if basarili_mi:
            messages.success(request, mesaj)
            if 'reset_email' in request.session:
                del request.session['reset_email']
            return redirect('giris_yap')
        else:
            messages.error(request, mesaj)

    return render(request, 'accounts/reset_password.html', {'email': email})


@login_required(login_url='giris_yap')
def profil_view(request):
    # Eğer sistemde eski bir hesapsa ve profili yoksa çökmesin diye otomatik oluşturuyoruz
    profil, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Kullanıcı fotoğraf yüklediyse
        if 'profile_picture' in request.FILES:
            profil.profile_picture = request.FILES['profile_picture']
            profil.save()
            messages.success(request, "Profil fotoğrafın jilet gibi güncellendi!")
            return redirect('profil_sayfasi')  # urls.py'daki ismin neyse o kalsın

    # 🚀 İŞTE YENİ EKLENEN FAVORİLER KISMI
    # select_related('recipe') ile veritabanını yormadan tarif detaylarını da hızlıca çekiyoruz
    kullanici_favorileri = Favorite.objects.filter(user=request.user).select_related('recipe').order_by('-created_at')

    # 📦 PAKETİ HAZIRLIYORUZ: Hem profil bilgilerini hem favorileri HTML'e gönderiyoruz
    context = {
        'profil': profil,
        'favoriler': kullanici_favorileri
    }

    return render(request, 'accounts/profile.html', context)


@login_required(login_url='/hesap/giris/')
def dashboard_view(request):
    # Tüm maliyetleri eskiden yeniye çekiyoruz (Grafik soldan sağa aksın diye)
    maliyetler = MarketCost.objects.filter(user=request.user).order_by('tarih')

    # Verileri tariflere göre grupla
    gruplanmis_maliyetler = defaultdict(list)
    for m in maliyetler:
        gruplanmis_maliyetler[m.recipe].append(m)

    # Template'e daha rahat göndermek için listeye çevirelim
    tarif_listesi = []
    for recipe, costs in gruplanmis_maliyetler.items():
        tarif_listesi.append({
            'recipe': recipe,
            'costs': costs,
            'son_maliyet': costs[-1],  # Listenin en sonundaki en güncelidir
        })

    context = {
        'tarif_listesi': tarif_listesi
    }
    maliyetler = MarketCost.objects.filter(user=request.user).order_by('-tarih')[:10]  # Son 10 işlem

    context = {
        'tarif_listesi': tarif_listesi,
        'maliyetler': maliyetler,  # Bunu context'e eklediğinden emin ol!
    }
    return render(request, 'dashboard.html', context)


# Diğer view fonksiyonlarının altına ekle:
def sifre_degistir_view(request):
    if request.method == 'POST':
        eski_sifre = request.POST.get('eski_sifre')
        yeni_sifre = request.POST.get('yeni_sifre')
        yeni_sifre_tekrar = request.POST.get('yeni_sifre_tekrar')

        # 1. KONTROL: Eski şifre doğru mu?
        if not request.user.check_password(eski_sifre):
            messages.error(request, "Mevcut şifrenizi yanlış girdiniz! Lütfen tekrar deneyin.")
            return redirect('profil_sayfasi')

        # 2. KONTROL: Yeni şifreler aynı mı? (Senin şifre sıfırlama stiline birebir uygun)
        if yeni_sifre != yeni_sifre_tekrar:
            messages.error(request, "Girdiğiniz yeni şifreler birbiriyle eşleşmiyor! Lütfen tekrar deneyin.")
            return redirect('profil_sayfasi')

        # 3. KONTROL: Yeni şifre, mevcut şifreyle aynı mı?
        if request.user.check_password(yeni_sifre):
            messages.error(request,
                           "Girdiğiniz yeni şifre mevcut şifrenizle aynı olamaz. Lütfen farklı bir şifre belirleyin.")
            return redirect('profil_sayfasi')

        # 4. KONTROL: Yeni şifre son 2 şifreyle aynı mı?
        try:
            eski_sifreler = PasswordHistory.objects.filter(user=request.user).order_by('-id')[:2]
            for gecmis in eski_sifreler:
                if check_password(yeni_sifre, gecmis.password):
                    messages.error(request,
                                   "Yeni şifreniz son kullandığınız 2 şifreden biriyle aynı olamaz. Lütfen farklı bir şifre belirleyin.")
                    return redirect('profil_sayfasi')
        except Exception as e:
            print(f"Şifre geçmişi kontrol edilemedi: {e}")

        # Başarılı kayıt işlemleri
        request.user.set_password(yeni_sifre)
        request.user.save()

        # Geçmişe kaydet
        try:
            PasswordHistory.objects.create(user=request.user, password=request.user.password)
        except Exception as e:
            print(f"Şifre geçmişe kaydedilemedi: {e}")

        # Oturumun düşmesini engelle
        update_session_auth_hash(request, request.user)

        messages.success(request, "Şifreniz başarıyla güncellenmiştir.")
        return redirect('profil_sayfasi')

    return redirect('profil_sayfasi')


@login_required(login_url='giris_yap')  # Güvenlik: Sadece giriş yapanlar değiştirebilir
def bio_guncelle_view(request):
    if request.method == 'POST':
        # .strip() komutu çok hayat kurtarır! Kullanıcı kazara sadece boşluk
        # tuşuna basıp gönderdiyse o görünmez boşlukları temizler.
        yeni_bio = request.POST.get('bio', '').strip()

        # Kullanıcının profiline ulaşıp bio'yu güncelliyoruz
        profile = request.user.profile
        profile.bio = yeni_bio
        profile.save()

        messages.success(request, "Biyografin başarıyla güncellendi şefim!")
        return redirect('profil_sayfasi')

    return redirect('profil_sayfasi')
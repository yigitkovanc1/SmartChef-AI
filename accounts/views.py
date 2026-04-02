from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .services import create_user_account, authenticate_user, send_password_reset_code, reset_user_password


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
            messages.error(request, request)

    return render(request, 'accounts/register.html')


def giris_yap_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')  # E-posta ile giriş
        sifre = request.POST.get('sifre')

        basarili_mi, user, mesaj = authenticate_user(request, email, sifre)

        if basarili_mi:
            login(request, user)
            return redirect('ana_sayfa')
        else:
            messages.error(request, mesaj)

    return render(request, 'accounts/login.html')


def cikis_yap_view(request):
    logout(request)
    return redirect('giris_yap')


@login_required(login_url='giris_yap')
def ana_sayfa_view(request):
    return render(request, 'accounts/chat.html')


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


@login_required
def profil_view(request):
    # Kullanıcının favorilerini çekiyoruz
    favoriler = request.user.favorites.all()  # related_name='favorites' demiştik
    # Favori nesnelerinin içinden asıl tarif (recipe) nesnelerini ayıklıyoruz
    favori_tarifler = [f.recipe for f in favoriler]

    return render(request, 'accounts/profile.html', {'favori_tarifler': favori_tarifler})
# SmartChef AI 🍳🤖

SmartChef AI, evdeki mevcut malzemeleri en verimli şekilde değerlendirerek yemek israfını önlemeyi amaçlayan, yapay zeka destekli bir mutfak ve maliyet yönetimi asistanıdır. MAT132 dersi projesi olarak temelleri atılan bu platform, kullanıcıların mutfaklarındaki malzemelerle bütçe dostu, ölçülü ve lezzetli tarifler oluşturmasına olanak tanır.

assets/giris_ve_kayit_sayfasi.png
assets/anasayfa.png

## 🚀 Proje Vizyonu

Günümüzde gıda israfı, hem ekolojik hem de ekonomik açıdan büyük bir problem teşkil etmektedir. SmartChef AI; "Bugün ne pişirsem?" sorusunu ortadan kaldırırken, evdeki malzemelerin çöpe gitmesini engeller. Hedefimiz, profesyonel mutfak hassasiyetini (gram/mililitre bazlı ölçümler) ev kullanıcılarına sunarak, porsiyon bazlı maliyet analizleriyle ev ekonomisine doğrudan katkı sağlamaktır.

## ✨ Temel Özellikler

* **🪄 Sihirli Dolap:** Sisteme girdiğiniz mevcut malzemeleri analiz ederek, ekstra alışverişe gerek kalmadan yapabileceğiniz en uygun yemekleri otomatik olarak tespit eder.
* **🧠 Gemini AI ile Akıllı Tarifler:** Google Gemini API entegrasyonu sayesinde, elinizdeki kısıtlı malzemelerle bile yaratıcı, lezzetli ve atıksız tarif alternatifleri üretir.
 assets/chat_tarif.png
* **⚖️ Metrik Sistem Hassasiyeti:** "Göz kararı" kavramını geride bırakarak, gr ve ml tabanlı kesin ölçümlerle tutarlı sonuçlar veren tarifler oluşturur.
  assets/tarif_defteri.png
* **💰 Ekonomik Maliyet Hesaplama:** Kullanılan malzemelerin güncel verilerine dayanarak yemeğin porsiyon başına düşen maliyetini hesaplar, bütçe dostu mutfak yönetimi sağlar.
  assets/chat_maliyet.png
  assets/maliyet_dashboard.png
  assets/maliyet_ligi.png

## 🛠️ Teknolojiler (Tech Stack)

Bu proje, güçlü bir backend mimarisi ve kullanıcı dostu bir arayüz ile geliştirilmiştir:

* **Backend:** Django, Python
* **Frontend:** Bootstrap, HTML5, CSS3 
* **Veritabanı:** Django
* **Yapay Zeka:** Google Gemini API

## ⚙️ Kurulum (Installation)

Projeyi yerel ortamınızda (local) çalıştırmak için aşağıdaki adımları izleyebilirsiniz.

1. **Depoyu Klonlayın:**
   ```bash
   git clone [https://github.com/kullaniciadi/smartchef-ai.git](https://github.com/kullaniciadi/smartchef-ai.git)
   cd smartchef-ai

Sanal Ortam (Virtual Environment) Oluşturun ve Aktif Edin: 
python -m venv venv
# Windows için:
venv\Scripts\activate
# macOS/Linux için:
source venv/bin/activate


Gerekli Kütüphaneleri Yükleyin: 
pip install -r requirements.txt

Çevresel Değişkenleri (Environment Variables) Ayarlayın: Ana dizinde bir .env dosyası oluşturun ve aşağıdaki anahtarları kendi bilgilerinizle doldurun: 

SECRET_KEY=your_django_secret_key
DEBUG=True
GEMINI_API_KEY=your_gemini_api_key

Veritabanı Migrasyonlarını Gerçekleştirin: 
python manage.py migrate

Geliştirme Sunucusunu Başlatın:
python manage.py runserver
Tarayıcınızda http://127.0.0.1:8000/ adresine giderek uygulamaya erişebilirsiniz. 

💡 Kullanım (Usage)
Uygulamaya giriş yaptıktan sonra Sihirli Dolap sekmesine gidin.
Mutfakta halihazırda bulunan malzemelerinizi (gr veya ml cinsinden miktarlarıyla birlikte) sisteme ekleyin.
Gemini AI tarafından size özel oluşturulan tarifleri listeleyin.
Seçtiğiniz tarifin detaylarına girerek adım adım yapılışını ve porsiyon başına düşen maliyet analizini inceleyin.
👨‍💻 Geliştiriciler
Yiğit Kovancı

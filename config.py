# =====================================================
# ⚙️ WOWSY BOT - AYARLAR VE YAPILANDIRMA
# =====================================================

import os
import json
from dotenv import load_dotenv

# .env dosyasını yükle (EN ÖNCE!)
load_dotenv()

# =====================================================
# 🔑 TOKENLAR VE API ANAHTARLARI
# =====================================================

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# =====================================================
# 👑 PATRON (SAHİP) AYARLARI
# =====================================================

PATRON_ID = 692517100144558090  # Senin Discord ID'n

# =====================================================
# 🎵 MÜZİK AYARLARI
# =====================================================

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin',
    'options': '-vn -bufsize 64k'
}

# =====================================================
# 🍪 YOUTUBE ÇEREZ AYARLARI (Bot korumasını aşmak için)
# =====================================================

# Yöntem 1: Tarayıcıdan otomatik çerez al (Sunucuda tarayıcı yoksa None)
COOKIE_BROWSER = None

# Yöntem 2: cookies.txt dosyasından çerez al (AKTİF)
COOKIE_FILE = "cookies.txt"

# Yöntem 3: OAuth2 (Artık desteklenmiyor)
YOUTUBE_OAUTH2 = False

# =====================================================
# 🔥 FIREBASE BAĞLANTISI
# =====================================================

import firebase_admin
from firebase_admin import credentials, firestore

db = None
economy_ref = None
warnings_ref = None

# Önce JSON dosyasından dene
if os.path.exists('firebase_key.json'):
    try:
        cred = credentials.Certificate('firebase_key.json')
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        economy_ref = db.collection('economy')
        warnings_ref = db.collection('warnings')
        print("✅ Firebase bağlandı! (JSON dosyasından)")
    except Exception as e:
        print(f"❌ Firebase hatası: {e}")

# Sonra environment variable'dan dene
elif os.getenv('GOOGLE_CREDENTIALS'):
    try:
        cred_dict = json.loads(os.getenv('GOOGLE_CREDENTIALS'))
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        economy_ref = db.collection('economy')
        warnings_ref = db.collection('warnings')
        print("✅ Firebase bağlandı! (ENV'den)")
    except Exception as e:
        print(f"❌ Firebase hatası: {e}")
else:
    print("⚠️ Firebase credentials bulunamadı! Veriler kaydedilmeyecek.")

# =====================================================
# 🤖 GROQ AI BAĞLANTISI
# =====================================================

groq_client = None

if GROQ_API_KEY:
    try:
        from groq import Groq
        groq_client = Groq(api_key=GROQ_API_KEY)
        print("✅ Groq AI aktif!")
    except Exception as e:
        print(f"⚠️ Groq AI başlatılamadı: {e}")
        groq_client = None
else:
    print("⚠️ GROQ_API_KEY bulunamadı! AI komutları çalışmayacak.")

# =====================================================
# 📊 DURUM KONTROLÜ
# =====================================================

def durum_ozeti():
    """Bot başlarken durum özeti yazdır"""
    # YouTube çerez durumu
    if COOKIE_BROWSER:
        yt_durum = f"✅ Tarayıcı ({COOKIE_BROWSER})"
    elif COOKIE_FILE:
        if os.path.exists(COOKIE_FILE):
            yt_durum = f"✅ Dosya ({COOKIE_FILE})"
        else:
            yt_durum = f"❌ Dosya bulunamadı ({COOKIE_FILE})"
    elif YOUTUBE_OAUTH2:
        yt_durum = "⚠️ OAuth2 (desteklenmiyor)"
    else:
        yt_durum = "⚠️ Çerez yok (engellenebilir)"

    print("")
    print("=" * 50)
    print("📊 YAPILANDIRMA DURUMU:")
    print(f"   ├ Discord Token: {'✅ Var' if DISCORD_TOKEN else '❌ Yok'}")
    print(f"   ├ Firebase:      {'✅ Bağlı' if db else '❌ Bağlı Değil'}")
    print(f"   ├ Groq AI:       {'✅ Aktif' if groq_client else '⚪ Pasif'}")
    print(f"   ├ YouTube Çerez: {yt_durum}")
    print(f"   └ Patron ID:     {PATRON_ID}")
    print("=" * 50)
    print("")

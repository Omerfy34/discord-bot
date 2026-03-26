# =====================================================
# ⚙️ WOWSY BOT - AYARLAR VE YAPILANDIRMA
# =====================================================

import os
import json
from dotenv import load_dotenv

# .env dosyasını yükle
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
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -filter:a "volume=0.5"'
}

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
else:
    print("⚠️ GROQ_API_KEY bulunamadı! AI komutları çalışmayacak.")

# =====================================================
# 📊 DURUM KONTROLÜ
# =====================================================

def durum_ozeti():
    """Bot başlarken durum özeti yazdır"""
    print("")
    print("=" * 50)
    print("📊 YAPILANDIRMA DURUMU:")
    print(f"   ├ Discord Token: {'✅ Var' if DISCORD_TOKEN else '❌ Yok'}")
    print(f"   ├ Firebase:      {'✅ Bağlı' if db else '❌ Bağlı Değil'}")
    print(f"   ├ Groq AI:       {'✅ Aktif' if groq_client else '⚪ Pasif'}")
    print(f"   └ Patron ID:     {PATRON_ID}")
    print("=" * 50)
    print("")
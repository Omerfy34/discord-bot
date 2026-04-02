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
# 🍪 YOUTUBE ÇEREZ AYARLARI
# =====================================================

COOKIE_BROWSER = None
COOKIE_FILE = os.getenv('COOKIE_FILE', 'cookies.txt')

# Tam yola çevir
if COOKIE_FILE and not COOKIE_FILE.startswith('/'):
    COOKIE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), COOKIE_FILE)

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
# 🔧 YARDIMCI FONKSİYONLAR
# =====================================================

def check_youtube_cookies():
    """YouTube çerez durumunu kontrol et"""
    if COOKIE_FILE and os.path.exists(COOKIE_FILE):
        try:
            with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = [l for l in content.split('\n') if l.strip() and not l.startswith('#')]
                return True, f"{len(lines)} çerez"
        except Exception as e:
            return False, f"Okuma hatası: {e}"
    else:
        return False, "Dosya bulunamadı"

# =====================================================
# 📊 DURUM KONTROLÜ
# =====================================================

def durum_ozeti():
    """Bot başlarken durum özeti yazdır"""

    # YouTube çerez durumu
    if COOKIE_FILE and os.path.exists(COOKIE_FILE):
        cookie_ok, cookie_msg = check_youtube_cookies()
        yt_durum = f"✅ Dosya ({cookie_msg})"
    else:
        yt_durum = "⚠️ Çerez yok"

    print("")
    print("=" * 50)
    print("📊 YAPILANDIRMA DURUMU:")
    print(f"   ├ Discord Token: {'✅ Var' if DISCORD_TOKEN else '❌ Yok'}")
    print(f"   ├ Firebase:      {'✅ Bağlı' if db else '⚪ Bağlı Değil'}")
    print(f"   ├ Groq AI:       {'✅ Aktif' if groq_client else '⚪ Pasif'}")
    print(f"   ├ YouTube Çerez: {yt_durum}")
    print(f"   └ Patron ID:     {PATRON_ID}")
    print("=" * 50)
    print("")

# =====================================================
# 🚀 BAŞLANGIÇ KONTROLÜ
# =====================================================

def baslangic_kontrolu():
    """Bot başlamadan önce kontrolleri yap"""

    hatalar = []

    # Token kontrolü
    if not DISCORD_TOKEN:
        hatalar.append("DISCORD_TOKEN bulunamadı!")

    # FFmpeg kontrolü
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode != 0:
            hatalar.append("FFmpeg çalışmıyor!")
    except FileNotFoundError:
        hatalar.append("FFmpeg yüklü değil!")
    except Exception:
        pass  # İgnore

    # yt-dlp kontrolü
    try:
        import yt_dlp
    except ImportError:
        hatalar.append("yt-dlp yüklü değil!")

    # Hata varsa
    if hatalar:
        print("")
        print("🔴 KRİTİK HATALAR:")
        for h in hatalar:
            print(f"   ❌ {h}")
        print("")
        return False

    return True

# =====================================================
# 📋 EXPORT
# =====================================================

__all__ = [
    'DISCORD_TOKEN',
    'GROQ_API_KEY',
    'PATRON_ID',
    'FFMPEG_OPTIONS',
    'COOKIE_BROWSER',
    'COOKIE_FILE',
    'db',
    'economy_ref',
    'warnings_ref',
    'groq_client',
    'durum_ozeti',
    'baslangic_kontrolu',
    'check_youtube_cookies',
]

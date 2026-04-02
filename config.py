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
# 🎵 MÜZİK AYARLARI (GELİŞMİŞ)
# =====================================================

FFMPEG_OPTIONS = {
    'before_options': (
        '-reconnect 1 '
        '-reconnect_streamed 1 '
        '-reconnect_delay_max 5 '
        '-reconnect_at_eof 1 '
        '-nostdin '
        '-loglevel error'
    ),
    'options': (
        '-vn '
        '-filter:a "volume=0.5" '  # Ses seviyesi %50
        '-bufsize 128k '
        '-ar 48000 '  # Sampling rate
        '-ac 2 '      # Stereo
        '-b:a 128k'   # Bitrate
    )
}

# =====================================================
# 🍪 YOUTUBE ÇEREZ AYARLARI (Bot korumasını aşmak için)
# =====================================================

# ✅ Yöntem 1: Tarayıcıdan otomatik çerez al
# VDS'de çalışmaz (GUI tarayıcı yok)
# Windows/macOS'ta: "chrome", "firefox", "edge", "safari"
COOKIE_BROWSER = os.getenv('COOKIE_BROWSER', None)

# ✅ Yöntem 2: cookies.txt dosyasından çerez al (ÖNERİLEN)
# VDS'de tam yol kullanın: "/root/cookies.txt" veya "/home/user/cookies.txt"
COOKIE_FILE = os.getenv('COOKIE_FILE', 'cookies.txt')

# ⚠️ Çerez dosyası otomatik kontrol
if COOKIE_FILE and not COOKIE_FILE.startswith('/'):
    # Göreceli yol ise mutlak yola çevir
    COOKIE_FILE = os.path.abspath(COOKIE_FILE)

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
# 🔧 yt-dlp AYARLARI (Detaylı)
# =====================================================

def get_ytdlp_version():
    """yt-dlp versiyonunu kontrol et"""
    try:
        import yt_dlp
        return yt_dlp.version.__version__
    except:
        return "Bilinmiyor"

# =====================================================
# 📊 DURUM KONTROLÜ (GELİŞMİŞ)
# =====================================================

def durum_ozeti():
    """Bot başlarken durum özeti yazdır"""
    
    # YouTube çerez durumu
    yt_durum = "❌ Çerez yok"
    yt_detay = ""
    
    if COOKIE_BROWSER:
        yt_durum = f"✅ Tarayıcı"
        yt_detay = f"({COOKIE_BROWSER})"
    elif COOKIE_FILE:
        if os.path.exists(COOKIE_FILE):
            file_size = os.path.getsize(COOKIE_FILE)
            yt_durum = "✅ Dosya"
            yt_detay = f"({file_size} bytes)"
        else:
            yt_durum = "❌ Dosya yok"
            yt_detay = f"({COOKIE_FILE})"
    
    # yt-dlp versiyonu
    ytdlp_version = get_ytdlp_version()
    
    # FFmpeg kontrolü
    ffmpeg_durum = "✅ Mevcut" if os.system("ffmpeg -version > /dev/null 2>&1") == 0 else "❌ Bulunamadı"
    
    print("")
    print("=" * 60)
    print("🎵 WOWSY BOT - YAPILANDIRMA DURUMU")
    print("=" * 60)
    print("")
    print("🔑 BAĞLANTILAR:")
    print(f"   ├─ Discord Token:    {'✅ Var (' + DISCORD_TOKEN[:20] + '...)' if DISCORD_TOKEN else '❌ Yok'}")
    print(f"   ├─ Firebase:         {'✅ Bağlı' if db else '❌ Bağlı Değil'}")
    print(f"   └─ Groq AI:          {'✅ Aktif' if groq_client else '⚪ Pasif'}")
    print("")
    print("🎵 MÜZİK SİSTEMİ:")
    print(f"   ├─ FFmpeg:           {ffmpeg_durum}")
    print(f"   ├─ yt-dlp:           v{ytdlp_version}")
    print(f"   ├─ YouTube Çerez:    {yt_durum} {yt_detay}")
    print(f"   └─ Çerez Yolu:       {COOKIE_FILE if COOKIE_FILE else 'Yok'}")
    print("")
    print("👑 YETKİLENDİRME:")
    print(f"   └─ Patron ID:        {PATRON_ID}")
    print("")
    print("=" * 60)
    
    # ⚠️ Uyarılar
    warnings = []
    
    if not DISCORD_TOKEN:
        warnings.append("❌ DISCORD_TOKEN eksik! Bot başlamayacak.")
    
    if not db:
        warnings.append("⚠️ Firebase bağlı değil! Veriler kaydedilmeyecek.")
    
    if COOKIE_FILE and not os.path.exists(COOKIE_FILE):
        warnings.append(f"⚠️ Çerez dosyası bulunamadı: {COOKIE_FILE}")
        warnings.append("   → YouTube bot koruması nedeniyle müzik çalışmayabilir!")
    
    if not groq_client:
        warnings.append("⚪ Groq AI pasif. AI komutları çalışmayacak.")
    
    if os.system("ffmpeg -version > /dev/null 2>&1") != 0:
        warnings.append("❌ FFmpeg bulunamadı! Müzik çalmaz.")
    
    if warnings:
        print("⚠️ UYARILAR:")
        for w in warnings:
            print(f"   {w}")
        print("")
        print("=" * 60)
    
    print("")


# =====================================================
# 🛠️ YARDIMCI FONKSİYONLAR
# =====================================================

def check_youtube_cookies():
    """YouTube çerez durumunu detaylı kontrol et"""
    if COOKIE_FILE and os.path.exists(COOKIE_FILE):
        try:
            with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Netscape formatı kontrolü
                if not content.startswith('# Netscape HTTP Cookie File'):
                    return False, "Geçersiz format (Netscape formatı olmalı)"
                
                # youtube.com çerezleri var mı?
                if 'youtube.com' not in content.lower():
                    return False, "youtube.com çerezleri bulunamadı"
                
                # Satır sayısı
                lines = [l for l in content.split('\n') if l.strip() and not l.startswith('#')]
                
                return True, f"{len(lines)} çerez bulundu"
        except Exception as e:
            return False, f"Okuma hatası: {e}"
    else:
        return False, "Dosya bulunamadı"


def create_sample_env():
    """Örnek .env dosyası oluştur"""
    sample = """# =====================================================
# 🎵 WOWSY BOT - ENVIRONMENT VARIABLES
# =====================================================

# Discord Bot Token (https://discord.com/developers/applications)
DISCORD_TOKEN=your_discord_token_here

# Groq AI API Key (https://console.groq.com)
GROQ_API_KEY=your_groq_api_key_here

# YouTube Çerez Ayarları
COOKIE_BROWSER=chrome
COOKIE_FILE=/root/cookies.txt

# Firebase Credentials (JSON formatında)
# GOOGLE_CREDENTIALS={"type":"service_account",...}
"""
    
    if not os.path.exists('.env'):
        with open('.env.example', 'w', encoding='utf-8') as f:
            f.write(sample)
        print("✅ .env.example dosyası oluşturuldu!")


# =====================================================
# 🚀 BAŞLANGIÇ KONTROLÜ
# =====================================================

def baslangic_kontrolu():
    """Bot başlamadan önce tüm gereksinimleri kontrol et"""
    
    hatalar = []
    uyarilar = []
    
    # Kritik kontroller
    if not DISCORD_TOKEN:
        hatalar.append("DISCORD_TOKEN bulunamadı!")
    
    # FFmpeg kontrolü
    if os.system("ffmpeg -version > /dev/null 2>&1") != 0:
        hatalar.append("FFmpeg yüklü değil!")
    
    # yt-dlp kontrolü
    try:
        import yt_dlp
    except ImportError:
        hatalar.append("yt-dlp yüklü değil! (pip install yt-dlp)")
    
    # Uyarılar
    if not db:
        uyarilar.append("Firebase bağlı değil")
    
    cookie_ok, cookie_msg = check_youtube_cookies()
    if not cookie_ok:
        uyarilar.append(f"YouTube çerez sorunu: {cookie_msg}")
    
    # Sonuç
    if hatalar:
        print("🔴 KRİTİK HATALAR:")
        for h in hatalar:
            print(f"   ❌ {h}")
        print("\n⛔ Bot başlatılamaz!\n")
        return False
    
    if uyarilar:
        print("🟡 UYARILAR:")
        for u in uyarilar:
            print(f"   ⚠️ {u}")
        print("")
    
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

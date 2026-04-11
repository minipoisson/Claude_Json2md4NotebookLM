#!/usr/bin/env python3
"""
Claude_Json2md4NotebookLM
Converts Claude's exported conversations.json into sequential Markdown files
suitable for NotebookLM ingestion.

Usage:
    python Json2md4LM.py \
        [--input_file conversations.json] \
        [--output_file Claude_History.md] \
        [--limit 1000000]
"""

import argparse
import json
import locale
import os
import re
from datetime import datetime
from typing import Any

LAST_ENTRY_FILE = "last_entry_time.txt"

# Mapping from locale language names to ISO 639-1 codes
LANG_MAP = {
    "Arabic": "ar",
    "Bengali": "bn",
    "German": "de",
    "English": "en",
    "Spanish": "es",
    "Persian": "fa",
    "French": "fr",
    "Hindi": "hi",
    "Indonesian": "id",
    "Japanese": "ja",
    "Javanese": "jv",
    "Korean": "ko",
    "Marathi": "mr",
    "Malay": "ms",
    "Punjabi": "pa",
    "Portuguese": "pt",
    "Russian": "ru",
    "Swahili": "sw",
    "Tamil": "ta",
    "Telugu": "te",
    "Thai": "th",
    "Turkish": "tr",
    "Ukrainian": "uk",
    "Urdu": "ur",
    "Vietnamese": "vi",
    "Chinese_China": "zh_CN",
    "Chinese_Taiwan": "zh_TW",
}

TRANSLATIONS: dict[str, dict[str, str]] = {
    "ar": {
        "error_lang_detection": "خطأ أثناء اكتشاف لغة النظام: {}",
        "file_not_found": "خطأ: الملف غير موجود: {}",
        "json_decode_error": "خطأ في ترميز JSON: {}",
        "start_processing": "🚀 بدء المعالجة: جاري تحميل {}...",
        "written_to_file": "✅ تمت الكتابة: {}",
        "processing_complete": "✅ اكتمل: {0} تمت معالجته / {1} تم تخطيه (تزايدي)",
        "error_occurred": "حدث خطأ: {}",
        "untitled": "(بدون عنوان)",
        "label_created": "تاريخ الإنشاء",
        "label_updated": "تاريخ التحديث",
    },
    "bn": {
        "error_lang_detection": "সিস্টেম ভাষা সনাক্তকরণে ত্রুটি: {}",
        "file_not_found": "ত্রুটি: ফাইল পাওয়া যায়নি: {}",
        "json_decode_error": "JSON ডিকোড ত্রুটি: {}",
        "start_processing": "🚀 প্রক্রিয়াকরণ শুরু হচ্ছে: {} লোড হচ্ছে...",
        "written_to_file": "✅ লেখা হয়েছে: {}",
        "processing_complete": "✅ সম্পন্ন: {0} প্রক্রিয়াকৃত / {1} এড়ানো হয়েছে (বৃদ্ধিমূলক)",
        "error_occurred": "একটি ত্রুটি ঘটেছে: {}",
        "untitled": "(শিরোনামহীন)",
        "label_created": "তৈরি",
        "label_updated": "আপডেট",
    },
    "de": {
        "error_lang_detection": "Fehler bei der Erkennung der Systemsprache: {}",
        "file_not_found": "Fehler: Datei nicht gefunden: {}",
        "json_decode_error": "JSON-Decodierungsfehler: {}",
        "start_processing": "🚀 Verarbeitung gestartet: Lade {}...",
        "written_to_file": "✅ Geschrieben: {}",
        "processing_complete": "✅ Abgeschlossen: {0} verarbeitet / {1} übersprungen (inkrementell)",
        "error_occurred": "Ein Fehler ist aufgetreten: {}",
        "untitled": "(Ohne Titel)",
        "label_created": "Erstellt",
        "label_updated": "Aktualisiert",
    },
    "en": {
        "error_lang_detection": "Error while detecting system language: {}",
        "file_not_found": "Error: File not found: {}",
        "json_decode_error": "JSON decode error: {}",
        "start_processing": "🚀 Starting processing: Loading {}...",
        "written_to_file": "✅ Written: {}",
        "processing_complete": "✅ Done: {0} processed / {1} skipped (incremental)",
        "error_occurred": "An error occurred: {}",
        "untitled": "(Untitled)",
        "label_created": "Created",
        "label_updated": "Updated",
    },
    "es": {
        "error_lang_detection": "Error al detectar el idioma del sistema: {}",
        "file_not_found": "Error: Archivo no encontrado: {}",
        "json_decode_error": "Error al decodificar JSON: {}",
        "start_processing": "🚀 Iniciando procesamiento: Cargando {}...",
        "written_to_file": "✅ Escrito: {}",
        "processing_complete": "✅ Completado: {0} procesados / {1} omitidos (incremental)",
        "error_occurred": "Ocurrió un error: {}",
        "untitled": "(Sin título)",
        "label_created": "Creado",
        "label_updated": "Actualizado",
    },
    "fa": {
        "error_lang_detection": "خطا در شناسایی زبان سیستم: {}",
        "file_not_found": "خطا: فایل پیدا نشد: {}",
        "json_decode_error": "خطای رمزگشایی JSON: {}",
        "start_processing": "🚀 شروع پردازش: در حال بارگذاری {}...",
        "written_to_file": "✅ نوشته شد: {}",
        "processing_complete": "✅ تکمیل شد: {0} پردازش شد / {1} رد شد (افزایشی)",
        "error_occurred": "یک خطا رخ داد: {}",
        "untitled": "(بدون عنوان)",
        "label_created": "ایجاد شده",
        "label_updated": "به‌روز شده",
    },
    "fr": {
        "error_lang_detection": "Erreur lors de la détection de la langue du système : {}",
        "file_not_found": "Erreur : Fichier non trouvé : {}",
        "json_decode_error": "Erreur de décodage JSON : {}",
        "start_processing": "🚀 Démarrage du traitement : Chargement de {}...",
        "written_to_file": "✅ Écrit : {}",
        "processing_complete": "✅ Terminé : {0} traités / {1} ignorés (incrémentiel)",
        "error_occurred": "Une erreur est survenue : {}",
        "untitled": "(Sans titre)",
        "label_created": "Créé",
        "label_updated": "Mis à jour",
    },
    "hi": {
        "error_lang_detection": "त्रुटि: सिस्टम भाषा का पता लगाने में समस्या: {}",
        "file_not_found": "त्रुटि: फ़ाइल नहीं मिली: {}",
        "json_decode_error": "JSON डिकोड त्रुटि: {}",
        "start_processing": "🚀 प्रसंस्करण शुरू हो रहा है: {} लोड हो रहा है...",
        "written_to_file": "✅ लिखा गया: {}",
        "processing_complete": "✅ पूर्ण: {0} प्रोसेस / {1} छोड़े (वृद्धिशील)",
        "error_occurred": "एक त्रुटि आई: {}",
        "untitled": "(शीर्षक रहित)",
        "label_created": "बनाया",
        "label_updated": "अपडेट",
    },
    "id": {
        "error_lang_detection": "Error saat mendeteksi bahasa sistem: {}",
        "file_not_found": "Error: File tidak ditemukan: {}",
        "json_decode_error": "Error decode JSON: {}",
        "start_processing": "🚀 Memulai pemrosesan: Memuat {}...",
        "written_to_file": "✅ Ditulis: {}",
        "processing_complete": "✅ Selesai: {0} diproses / {1} dilewati (inkremental)",
        "error_occurred": "Terjadi kesalahan: {}",
        "untitled": "(Tanpa Judul)",
        "label_created": "Dibuat",
        "label_updated": "Diperbarui",
    },
    "ja": {
        "error_lang_detection": "システム言語の検出中にエラーが発生しました: {}",
        "file_not_found": "エラー: ファイルが見つかりません: {}",
        "json_decode_error": "JSONデコードエラー: {}",
        "start_processing": "🚀 処理開始: {} を読み込み中...",
        "written_to_file": "✅ 出力しました: {}",
        "processing_complete": "✅ 完了しました: {0} 件処理 / {1} 件スキップ（差分）",
        "error_occurred": "エラーが発生しました: {}",
        "untitled": "（無題）",
        "label_created": "作成",
        "label_updated": "更新",
    },
    "jv": {
        "error_lang_detection": "Kesalahan saat mendeteksi bahasa sistem: {}",
        "file_not_found": "Kesalahan: Berkas tidak ditemukan: {}",
        "json_decode_error": "Kesalahan dekode JSON: {}",
        "start_processing": "🚀 Memulai pemrosesan: Memuat {}...",
        "written_to_file": "✅ Ditulis: {}",
        "processing_complete": "✅ Selesai: {0} diproses / {1} dilangkahi (tambahan)",
        "error_occurred": "Terjadi kesalahan: {}",
        "untitled": "(Tanpa Judul)",
        "label_created": "Digawe",
        "label_updated": "Diperbarui",
    },
    "ko": {
        "error_lang_detection": "시스템 언어 설정 감지 중 오류 발생: {}",
        "file_not_found": "오류: 파일을 찾을 수 없습니다: {}",
        "json_decode_error": "JSON 디코드 오류: {}",
        "start_processing": "🚀 처리 시작: {} 로드 중...",
        "written_to_file": "✅ 작성되었습니다: {}",
        "processing_complete": "✅ 완료: {0}개 처리 / {1}개 건너뜀 (증분)",
        "error_occurred": "오류가 발생했습니다: {}",
        "untitled": "(제목 없음)",
        "label_created": "생성",
        "label_updated": "업데이트",
    },
    "mr": {
        "error_lang_detection": "त्रुटी: सिस्टम भाषा ओळखण्यात समस्या: {}",
        "file_not_found": "त्रुटी: फाइल सापडली नाही: {}",
        "json_decode_error": "JSON डिकोड त्रुटी: {}",
        "start_processing": "🚀 प्रक्रिया सुरू होणार आहे: {} लोड होत आहे...",
        "written_to_file": "✅ लिहिले: {}",
        "processing_complete": "✅ पूर्ण झाले: {0} प्रक्रिया केली / {1} वगळले (वृद्धिशील)",
        "error_occurred": "एक त्रुटी आली आहे: {}",
        "untitled": "(शीर्षकरहित)",
        "label_created": "तयार केले",
        "label_updated": "अद्यतनित",
    },
    "ms": {
        "error_lang_detection": "Ralat semasa mengesan bahasa sistem: {}",
        "file_not_found": "Ralat: Fail tidak dijumpai: {}",
        "json_decode_error": "Ralat nyahkod JSON: {}",
        "start_processing": "🚀 Memulakan pemprosesan: Memuat {}...",
        "written_to_file": "✅ Ditulis: {}",
        "processing_complete": "✅ Selesai: {0} diproses / {1} dilangkau (tambahan)",
        "error_occurred": "Ralat telah berlaku: {}",
        "untitled": "(Tanpa Tajuk)",
        "label_created": "Dibuat",
        "label_updated": "Dikemaskini",
    },
    "pa": {
        "error_lang_detection": "ਸਿਸਟਮ ਭਾਸ਼ਾ ਦਾ ਪਤਾ ਲਗਾਉਂਦੇ ਸਮੇਂ ਤਰੁੱਟੀ: {}",
        "file_not_found": "ਤਰੁੱਟੀ: ਫਾਇਲ ਨਹੀਂ ਮਿਲੀ: {}",
        "json_decode_error": "JSON ਡੀਕੋਡ ਤਰੁੱਟੀ: {}",
        "start_processing": "🚀 ਪ੍ਰੋਸੈੱਸਿੰਗ ਸ਼ੁਰੂ ਹੋ ਰਹੀ ਹੈ: {} ਲੋਡ ਹੋ ਰਿਹਾ ਹੈ...",
        "written_to_file": "✅ ਲਿਖਿਆ ਗਿਆ: {}",
        "processing_complete": "✅ ਮੁਕੰਮਲ: {0} ਪ੍ਰੋਸੈੱਸ / {1} ਛੱਡੇ ਗਏ (ਵਾਧੂ)",
        "error_occurred": "ਕੋਈ ਤਰੁੱਟੀ ਆਈ: {}",
        "untitled": "(ਬਿਨਾ ਸਿਰਲੇਖ)",
        "label_created": "ਬਣਾਇਆ",
        "label_updated": "ਅੱਪਡੇਟ ਕੀਤਾ",
    },
    "pt": {
        "error_lang_detection": "Erro ao detectar o idioma do sistema: {}",
        "file_not_found": "Erro: Arquivo não encontrado: {}",
        "json_decode_error": "Erro de decodificação JSON: {}",
        "start_processing": "🚀 Iniciando processamento: Carregando {}...",
        "written_to_file": "✅ Escrito: {}",
        "processing_complete": "✅ Concluído: {0} processados / {1} ignorados (incremental)",
        "error_occurred": "Ocorreu um erro: {}",
        "untitled": "(Sem título)",
        "label_created": "Criado",
        "label_updated": "Atualizado",
    },
    "ru": {
        "error_lang_detection": "Ошибка при определении языка системы: {}",
        "file_not_found": "Ошибка: Файл не найден: {}",
        "json_decode_error": "Ошибка декодирования JSON: {}",
        "start_processing": "🚀 Начало обработки: Загрузка {}...",
        "written_to_file": "✅ Записано: {}",
        "processing_complete": "✅ Завершено: {0} обработано / {1} пропущено (инкрементально)",
        "error_occurred": "Произошла ошибка: {}",
        "untitled": "(Без названия)",
        "label_created": "Создано",
        "label_updated": "Обновлено",
    },
    "sw": {
        "error_lang_detection": "Hitilafu wakati wa kugundua lugha ya mfumo: {}",
        "file_not_found": "Hitilafu: Faili haikupatikana: {}",
        "json_decode_error": "Hitilafu ya kutafsiri JSON: {}",
        "start_processing": "🚀 Kuanzia usindikaji: Inapakia {}...",
        "written_to_file": "✅ Imeandikwa: {}",
        "processing_complete": "✅ Imekamilika: {0} zilishughulikiwa / {1} zilirukwa (ziada)",
        "error_occurred": "Hitilafu imetokea: {}",
        "untitled": "(Bila Kichwa)",
        "label_created": "Imetengenezwa",
        "label_updated": "Imesasishwa",
    },
    "ta": {
        "error_lang_detection": "சிஸ்டம் மொழியை கண்டறிதலில் பிழை: {}",
        "file_not_found": "பிழை: கோப்பு காணப்படவில்லை: {}",
        "json_decode_error": "JSON குறியாக்க பிழை: {}",
        "start_processing": "🚀 செயலாக்கம் தொடங்கிறது: {} ஏற்றப்படுகிறது...",
        "written_to_file": "✅ எழுதப்பட்டது: {}",
        "processing_complete": "✅ முடிந்தது: {0} செயலாக்கப்பட்டது / {1} தவிர்க்கப்பட்டது (தொடர்ச்சியான)",
        "error_occurred": "ஒரு பிழை ஏற்பட்டது: {}",
        "untitled": "(தலைப்பு இல்லை)",
        "label_created": "உருவாக்கப்பட்டது",
        "label_updated": "புதுப்பிக்கப்பட்டது",
    },
    "te": {
        "error_lang_detection": "సిస్టమ్ భాషను గుర్తించడంలో లోపం: {}",
        "file_not_found": "లోపం: ఫైలు కనుగొనబడలేదు: {}",
        "json_decode_error": "JSON డీకోడ్ లోపం: {}",
        "start_processing": "🚀 ప్రాసెసింగ్ ప్రారంభం: {} లోడ్ అవుతుంది...",
        "written_to_file": "✅ రాయబడింది: {}",
        "processing_complete": "✅ పూర్తయింది: {0} ప్రాసెస్ చేయబడింది / {1} దాటవేయబడింది (పెరుగుదల)",
        "error_occurred": "లోపం సంభవించింది: {}",
        "untitled": "(శీర్షిక లేదు)",
        "label_created": "సృష్టించబడింది",
        "label_updated": "నవీకరించబడింది",
    },
    "th": {
        "error_lang_detection": "เกิดข้อผิดพลาดขณะตรวจสอบภาษาระบบ: {}",
        "file_not_found": "ข้อผิดพลาด: ไม่พบไฟล์: {}",
        "json_decode_error": "ข้อผิดพลาดในการถอดรหัส JSON: {}",
        "start_processing": "🚀 เริ่มการประมวลผล: กำลังโหลด {}...",
        "written_to_file": "✅ เขียนแล้ว: {}",
        "processing_complete": "✅ เสร็จสิ้น: {0} รายการที่ประมวลผล / {1} รายการที่ข้าม (เพิ่มเติม)",
        "error_occurred": "เกิดข้อผิดพลาด: {}",
        "untitled": "(ไม่มีชื่อ)",
        "label_created": "สร้าง",
        "label_updated": "อัปเดต",
    },
    "tr": {
        "error_lang_detection": "Sistem dili algılanırken hata oluştu: {}",
        "file_not_found": "Hata: Dosya bulunamadı: {}",
        "json_decode_error": "JSON kod çözme hatası: {}",
        "start_processing": "🚀 İşleme başlıyor: {} yükleniyor...",
        "written_to_file": "✅ Yazıldı: {}",
        "processing_complete": "✅ Tamamlandı: {0} işlendi / {1} atlandı (artımlı)",
        "error_occurred": "Bir hata oluştu: {}",
        "untitled": "(Başlıksız)",
        "label_created": "Oluşturuldu",
        "label_updated": "Güncellendi",
    },
    "uk": {
        "error_lang_detection": "Помилка під час визначення мови системи: {}",
        "file_not_found": "Помилка: Файл не знайдено: {}",
        "json_decode_error": "Помилка декодування JSON: {}",
        "start_processing": "🚀 Початок обробки: Завантаження {}...",
        "written_to_file": "✅ Записано: {}",
        "processing_complete": "✅ Завершено: {0} оброблено / {1} пропущено (інкрементально)",
        "error_occurred": "Сталася помилка: {}",
        "untitled": "(Без назви)",
        "label_created": "Створено",
        "label_updated": "Оновлено",
    },
    "ur": {
        "error_lang_detection": "سسٹم زبان کا پتہ لگانے میں خرابی: {}",
        "file_not_found": "خرابی: فائل نہیں ملی: {}",
        "json_decode_error": "JSON کی کوڈنگ کی خرابی: {}",
        "start_processing": "🚀 پراسیسنگ شروع ہو رہی ہے: {} لوڈ ہو رہا ہے...",
        "written_to_file": "✅ لکھ دیا گیا: {}",
        "processing_complete": "✅ مکمل ہو گیا: {0} پروسیس / {1} چھوڑے گئے (اضافی)",
        "error_occurred": "ایک خرابی پیش آئی: {}",
        "untitled": "(بے عنوان)",
        "label_created": "بنایا گیا",
        "label_updated": "اپ ڈیٹ کیا گیا",
    },
    "vi": {
        "error_lang_detection": "Lỗi khi phát hiện ngôn ngữ hệ thống: {}",
        "file_not_found": "Lỗi: Không tìm thấy tệp: {}",
        "json_decode_error": "Lỗi giải mã JSON: {}",
        "start_processing": "🚀 Bắt đầu xử lý: Đang tải {}...",
        "written_to_file": "✅ Đã ghi: {}",
        "processing_complete": "✅ Hoàn thành: {0} đã xử lý / {1} đã bỏ qua (tăng dần)",
        "error_occurred": "Đã xảy ra lỗi: {}",
        "untitled": "(Không có tiêu đề)",
        "label_created": "Đã tạo",
        "label_updated": "Đã cập nhật",
    },
    "zh_CN": {
        "error_lang_detection": "检测系统语言时出错：{}",
        "file_not_found": "错误：未找到文件：{}",
        "json_decode_error": "JSON 解码错误：{}",
        "start_processing": "🚀 开始处理：正在加载 {}...",
        "written_to_file": "✅ 已写入：{}",
        "processing_complete": "✅ 完成：{0} 条已处理 / {1} 条已跳过（增量）",
        "error_occurred": "发生错误：{}",
        "untitled": "（无标题）",
        "label_created": "创建",
        "label_updated": "更新",
    },
    "zh_TW": {
        "error_lang_detection": "檢測系統語言時出錯：{}",
        "file_not_found": "錯誤：未找到檔案：{}",
        "json_decode_error": "JSON 解碼錯誤：{}",
        "start_processing": "🚀 開始處理：正在載入 {}...",
        "written_to_file": "✅ 已寫入：{}",
        "processing_complete": "✅ 完成：{0} 條已處理 / {1} 條已跳過（增量）",
        "error_occurred": "發生錯誤：{}",
        "untitled": "（無標題）",
        "label_created": "建立",
        "label_updated": "更新",
    },
}


def get_system_language() -> str:
    """Detect the OS language setting and return an ISO 639-1 code."""
    try:
        lang_tuple = locale.getlocale()
        if lang_tuple[0]:
            lang_name = lang_tuple[0].split("_")[0]
            lang_code = LANG_MAP.get(lang_name, lang_name[:2].lower())
        else:
            lang_code = None

        if lang_code is None:
            return "en"

        if lang_code == "zh_CN" or lang_code == "zh-Hans" or lang_name == "Chinese_China":
            return "zh_CN"
        elif lang_code == "zh_TW" or lang_code == "zh-Hant" or lang_name == "Chinese_Taiwan":
            return "zh_TW"

        lang_code = lang_code.split("_")[0].split("-")[0].lower()
        if lang_code in TRANSLATIONS:
            return lang_code
        return "en"

    except Exception as e:
        error_msg = TRANSLATIONS.get("en", {}).get("error_lang_detection", "Error: {}")
        print(error_msg.format(e))
        return "en"


# Detect once at module load; avoids repeated locale.getlocale() calls in t()
_LANG: str = get_system_language()


def t(key: str, *args: Any) -> str:
    """Return a translated message for the current system language."""
    msg_map: dict[str, str] = TRANSLATIONS.get(_LANG, TRANSLATIONS["en"])
    msg: str = msg_map.get(key, TRANSLATIONS["en"].get(key, key))
    if args:
        try:
            return msg.format(*args)
        except IndexError:
            return msg
    return msg


def load_last_entry_time(path: str) -> datetime | None:
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read().strip()
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def save_last_entry_time(path: str, dt: datetime) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(dt.isoformat())


def parse_iso(dt_str: str) -> datetime:
    """Convert an ISO 8601 string to a datetime object (timezone-aware)"""
    return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))


def clean_text(text: str) -> str:
    """Strip HTML tags and normalize whitespace"""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def conversation_to_markdown(conv: dict) -> str:
    """Convert a single conversation into a Markdown block"""
    title = conv.get("name") or t("untitled")
    created = conv.get("created_at", "")
    updated = conv.get("updated_at", "")
    messages = conv.get("chat_messages", [])

    lines = [
        f"## {title}",
        f"- {t('label_created')}: {created}",
        f"- {t('label_updated')}: {updated}",
        "",
    ]

    for msg in messages:
        sender = msg.get("sender", "unknown")
        text = clean_text(msg.get("text") or "")
        if not text:
            continue

        if sender == "human":
            prefix = "**Human:**"
        elif sender == "assistant":
            prefix = "**Claude:**"
        else:
            prefix = f"**{sender}:**"

        lines.append(f"{prefix}")
        lines.append(text)
        lines.append("")

    return "\n".join(lines) + "\n\n---\n\n"


def generate_output_path(base: str, index: int) -> str:
    root, ext = os.path.splitext(base)
    ext = ext or ".md"
    return f"{root}-{index:02d}{ext}"


def main():
    parser = argparse.ArgumentParser(
        description="Convert Claude history JSON to Markdown for NotebookLM"
    )
    parser.add_argument("--input_file", default="conversations.json")
    parser.add_argument("--output_file", default="Claude_History.md")
    parser.add_argument(
        "--limit", type=int, default=1_000_000, help="Max bytes per output file"
    )
    args = parser.parse_args()

    print(t("start_processing", args.input_file))

    if not os.path.exists(args.input_file):
        print(t("file_not_found", args.input_file))
        return

    with open(args.input_file, "r", encoding="utf-8") as f:
        try:
            conversations: list[dict] = json.load(f)
        except json.JSONDecodeError as e:
            print(t("json_decode_error", e))
            return

    # Sort by updated_at ascending (oldest first)
    conversations.sort(key=lambda c: c.get("updated_at", ""))

    last_time = load_last_entry_time(LAST_ENTRY_FILE)
    newest_time: datetime | None = None

    file_index = 0
    current_bytes = 0
    current_lines: list[str] = []
    processed = 0
    skipped = 0

    def flush(lines: list[str], index: int) -> None:
        path = generate_output_path(args.output_file, index)
        with open(path, "w", encoding="utf-8") as f:
            f.write("".join(lines))
        print(t("written_to_file", path))

    for conv in conversations:
        updated_str = conv.get("updated_at", "")
        try:
            updated_dt = parse_iso(updated_str)
        except (ValueError, AttributeError):
            updated_dt = None

        # Incremental update: skip conversations already processed last run
        if last_time and updated_dt and updated_dt <= last_time:
            skipped += 1
            continue

        block = conversation_to_markdown(conv)
        block_bytes = len(block.encode("utf-8"))

        # Check if output file size limit is exceeded
        if current_bytes + block_bytes > args.limit and current_lines:
            flush(current_lines, file_index)
            file_index += 1
            current_lines = []
            current_bytes = 0

        current_lines.append(block)
        current_bytes += block_bytes
        processed += 1

        if updated_dt:
            if newest_time is None or updated_dt > newest_time:
                newest_time = updated_dt

    if current_lines:
        flush(current_lines, file_index)

    if newest_time:
        save_last_entry_time(LAST_ENTRY_FILE, newest_time)

    print(t("processing_complete", processed, skipped))


if __name__ == "__main__":
    main()

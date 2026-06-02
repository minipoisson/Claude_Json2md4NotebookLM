from unittest.mock import patch
import convert_claude_history as ch


def _lang(locale_name):
    """Call get_system_language() with a mocked locale.getlocale result."""
    with patch("locale.getlocale", return_value=(locale_name, "UTF-8")):
        return ch.get_system_language()


def test_chinese_china():
    assert _lang("Chinese_China") == "zh_CN"


def test_chinese_taiwan():
    assert _lang("Chinese_Taiwan") == "zh_TW"


def test_japanese():
    assert _lang("Japanese_Japan") == "ja"


def test_english():
    assert _lang("English_United_States") == "en"


def test_unix_zh_cn():
    assert _lang("zh_CN") == "zh_CN"


def test_unix_zh_tw():
    assert _lang("zh_TW") == "zh_TW"


def test_unix_de_de():
    assert _lang("de_DE") == "de"


def test_unix_ja():
    assert _lang("ja_JP") == "ja"


def test_unknown_locale():
    assert _lang("Klingon_Qonos") == "en"


def test_none_locale():
    with patch("locale.getlocale", return_value=(None, None)):
        assert ch.get_system_language() == "en"

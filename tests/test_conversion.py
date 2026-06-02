import convert_claude_history as ch


# --- clean_text ---

def test_clean_text_strips_html():
    assert ch.clean_text("<b>hello</b>") == "hello"


def test_clean_text_strips_nested_html():
    assert ch.clean_text("<div><p>text</p></div>") == "text"


def test_clean_text_collapses_newlines():
    result = ch.clean_text("a\n\n\n\nb")
    assert "\n\n\n" not in result
    assert "a" in result and "b" in result


def test_clean_text_empty_string():
    assert ch.clean_text("") == ""


def test_clean_text_none():
    assert ch.clean_text(None) == ""


# --- conversation_to_markdown ---

def _make_conv(messages, name="Test Conv", updated="2024-01-15T10:00:00Z"):
    return {
        "name": name,
        "created_at": "2024-01-15T09:00:00Z",
        "updated_at": updated,
        "chat_messages": messages,
    }


def test_empty_message_skipped():
    conv = _make_conv([{"sender": "human", "text": "   ", "created_at": ""}])
    md = ch.conversation_to_markdown(conv)
    assert "**Human**" not in md


def test_none_text_message_skipped():
    conv = _make_conv([{"sender": "human", "text": None, "created_at": ""}])
    md = ch.conversation_to_markdown(conv)
    assert "**Human**" not in md


def test_human_message_rendered():
    conv = _make_conv([{"sender": "human", "text": "Hello there", "created_at": "2024-01-15T09:01:00Z"}])
    md = ch.conversation_to_markdown(conv)
    assert "**Human**" in md
    assert "Hello there" in md


def test_assistant_message_rendered():
    conv = _make_conv([{"sender": "assistant", "text": "Hi!", "created_at": "2024-01-15T09:01:05Z"}])
    md = ch.conversation_to_markdown(conv)
    assert "**Claude**" in md
    assert "Hi!" in md


def test_unknown_sender_rendered_verbatim():
    conv = _make_conv([{"sender": "system", "text": "Note", "created_at": ""}])
    md = ch.conversation_to_markdown(conv)
    assert "**system**" in md
    assert "Note" in md


def test_untitled_fallback():
    conv = _make_conv([], name=None)
    md = ch.conversation_to_markdown(conv)
    assert "## " in md
    assert "None" not in md


def test_empty_name_fallback():
    conv = _make_conv([], name="")
    md = ch.conversation_to_markdown(conv)
    assert "## " in md


def test_timestamp_in_message_prefix():
    conv = _make_conv([{"sender": "human", "text": "Hi", "created_at": "2024-01-15T09:01:00Z"}])
    md = ch.conversation_to_markdown(conv)
    assert "2024-01-15" in md


def test_header_contains_created_and_updated():
    conv = _make_conv([])
    md = ch.conversation_to_markdown(conv)
    assert "2024-01-15" in md


def test_separator_appended():
    conv = _make_conv([])
    md = ch.conversation_to_markdown(conv)
    assert md.endswith("---\n\n")

from utils.safety import format_summary_html, html_escape_join, html_escape_text, safe_url


def test_html_escape_text_escapes_external_markup():
    assert html_escape_text('<script>alert("x")</script>') == '&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;'


def test_safe_url_allows_only_http_urls():
    assert safe_url("https://example.com/paper?a=1&b=2") == "https://example.com/paper?a=1&amp;b=2"
    assert safe_url("http://example.com") == "http://example.com"
    assert safe_url("javascript:alert(1)") == ""
    assert safe_url("/relative/path") == ""


def test_format_summary_html_preserves_allowed_labels_after_escaping():
    raw = "📌 研究问题：<b>risk</b>\n💡 应用价值：useful"
    rendered = format_summary_html(raw)
    assert "<strong>📌 研究问题：</strong>" in rendered
    assert "&lt;b&gt;risk&lt;/b&gt;" in rendered
    assert "<br>" in rendered


def test_html_escape_join_filters_empty_values():
    assert html_escape_join(["A&B", "", None, "C<D"]) == "A&amp;B, C&lt;D"

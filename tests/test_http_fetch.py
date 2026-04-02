from news_sentiment.collectors.http import fetch_html


class DummyResponse:
    def __enter__(self) -> "DummyResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def read(self) -> bytes:
        return b"<html>ok</html>"


def test_fetch_html_passes_timeout_and_user_agent() -> None:
    captured: dict[str, object] = {}

    def fake_urlopen(request, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        return DummyResponse()

    html = fetch_html(
        "https://example.com/news",
        timeout_seconds=7,
        user_agent="news-sentiment-test/1.0",
        urlopen_func=fake_urlopen,
    )

    assert html == "<html>ok</html>"
    assert captured["timeout"] == 7
    assert captured["request"].headers["User-agent"] == "news-sentiment-test/1.0"

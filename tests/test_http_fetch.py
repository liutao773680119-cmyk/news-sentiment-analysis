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


def test_fetch_html_retries_before_succeeding() -> None:
    attempts = {"count": 0}
    sleeps: list[float] = []

    def fake_urlopen(request, timeout):
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise TimeoutError("timed out")
        return DummyResponse()

    html = fetch_html(
        "https://example.com/news",
        timeout_seconds=7,
        user_agent="news-sentiment-test/1.0",
        retry_count=2,
        backoff_seconds=0.5,
        urlopen_func=fake_urlopen,
        sleep_func=sleeps.append,
    )

    assert html == "<html>ok</html>"
    assert attempts["count"] == 3
    assert sleeps == [0.5, 1.0]


def test_fetch_html_merges_extra_headers() -> None:
    captured: dict[str, object] = {}

    def fake_urlopen(request, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        return DummyResponse()

    fetch_html(
        "https://example.com/news",
        timeout_seconds=7,
        user_agent="news-sentiment-test/1.0",
        extra_headers={
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://example.com/page",
        },
        urlopen_func=fake_urlopen,
    )

    assert captured["request"].headers["User-agent"] == "news-sentiment-test/1.0"
    assert captured["request"].headers["X-requested-with"] == "XMLHttpRequest"
    assert captured["request"].headers["Referer"] == "https://example.com/page"

from news_sentiment.cli import main
from news_sentiment.collectors.errors import CollectorParseError
from news_sentiment.collectors.miit import (
    collect_miit_news,
    extract_miit_build_request,
    parse_miit_build_response_html,
    parse_miit_news_list,
)


def test_parse_miit_news_list_extracts_news_rows() -> None:
    html = """
    <ul>
      <li>
        <a href="/xwfb/gxdt/art/2026/art_123.html" title="工信部召开新闻发布会部署算力基础设施">
          工信部召开新闻发布会部署算力基础设施
        </a>
        <span>2026-04-01</span>
      </li>
    </ul>
    """
    rows = parse_miit_news_list(html)
    assert len(rows) == 1
    assert rows[0].source == "miit"
    assert rows[0].title == "工信部召开新闻发布会部署算力基础设施"


def test_parse_miit_news_list_extracts_dynamic_rows() -> None:
    html = """
    <div class="page-content">
      <ul>
        <li class="cf">
          <a class="fl" href="http://www.miit.gov.cn/xwfb/xwfbh/bxwfbh/art/2026/art_abc.html" target="_blank" title="工业和信息化部举行新闻发布会">
            <i></i>工业和信息化部举行新闻发布会
          </a>
          <span class="fr">2026-04-02</span>
        </li>
      </ul>
    </div>
    """
    rows = parse_miit_news_list(html)
    assert len(rows) == 1
    assert rows[0].title == "工业和信息化部举行新闻发布会"


def test_extract_miit_build_request_from_shell_html() -> None:
    html = """
    <div class="clist_con">
      <script id="4e3a2e3cc51f4a7688f34405910955e2"
        src="/cms_files/default/script/AuthorizedRead/unitbuild.js?v=3.1.3-GXB"
        webId="8d828e408d90447786ddbe128d495e9e"
        parseType="buildstatic"
        url="/api-gateway/jpaas-publish-server/front/page/build/unit"
        queryData="{'parseType':'buildstatic','webId':'8d828e408d90447786ddbe128d495e9e','tplSetId':'209741b2109044b5b7695700b2bec37e','pageType':'column','tagId':'右侧内容','editType':'null','pageId':'ca517c97303b40cf80bd668b35f6148f'}">
      </script>
    </div>
    """
    build_url, params = extract_miit_build_request(html)
    assert build_url.endswith("/api-gateway/jpaas-publish-server/front/page/build/unit")
    assert params["parseType"] == "buildstatic"
    assert params["pageId"] == "ca517c97303b40cf80bd668b35f6148f"


def test_parse_miit_build_response_html_extracts_inner_html() -> None:
    payload = (
        '{"success":true,"data":{"html":"<ul><li class=\\"cf\\"><a href=\\"http://www.miit.gov.cn/xwfb/xwfbh/bxwfbh/art/2026/art_abc.html\\" '
        'title=\\"工业和信息化部举行新闻发布会\\">工业和信息化部举行新闻发布会</a><span class=\\"fr\\">2026-04-02</span></li></ul>"}}'
    )
    html = parse_miit_build_response_html(payload)
    assert "工业和信息化部举行新闻发布会" in html


def test_collect_miit_source_writes_raw_news(tmp_path, monkeypatch) -> None:
    html = """
    <ul>
      <li>
        <a href="/xwfb/gxdt/art/2026/art_123.html" title="工信部召开新闻发布会部署算力基础设施">
          工信部召开新闻发布会部署算力基础设施
        </a>
        <span>2026-04-01</span>
      </li>
    </ul>
    """

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.collectors.miit.fetch_miit_news_html",
        lambda url=None: html,
    )
    assert main(["collect", "--source", "miit"]) == 0
    assert (tmp_path / "data" / "raw" / "raw_news.jsonl").exists()


def test_collect_miit_news_raises_parse_error_on_unmatched_html(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.miit.fetch_miit_news_html",
        lambda url=None: "<html><body>unexpected</body></html>",
    )

    try:
        collect_miit_news()
    except CollectorParseError as exc:
        assert exc.source == "miit"
        assert exc.kind == "parse_error"
    else:
        raise AssertionError("Expected CollectorParseError")

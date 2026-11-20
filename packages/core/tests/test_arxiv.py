from datetime import datetime

from scholarlens_core.arxiv import extract_arxiv_id, parse_feed

SAMPLE = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/1706.03762v7</id>
    <published>2017-06-12T17:57:34Z</published>
    <title>Attention Is All
  You Need</title>
    <summary>  The dominant sequence
 transduction models.  </summary>
    <author><name>Ashish Vaswani</name></author>
    <author><name>Noam Shazeer</name></author>
    <link href="http://arxiv.org/abs/1706.03762v7" rel="alternate" type="text/html"/>
    <link title="pdf" href="http://arxiv.org/pdf/1706.03762v7" rel="related" type="application/pdf"/>
  </entry>
</feed>"""


def test_extract_new_style_id() -> None:
    assert extract_arxiv_id("http://arxiv.org/abs/1706.03762v7") == ("1706.03762", 7)


def test_extract_old_style_id() -> None:
    assert extract_arxiv_id("http://arxiv.org/abs/hep-th/9901001v1") == ("hep-th/9901001", 1)


def test_parse_feed_basic_fields() -> None:
    papers = parse_feed(SAMPLE)
    assert len(papers) == 1
    p = papers[0]
    assert p.arxiv_id == "1706.03762"
    assert p.version == 7
    assert p.title == "Attention Is All You Need"
    assert p.abstract == "The dominant sequence transduction models."
    assert p.authors == ["Ashish Vaswani", "Noam Shazeer"]
    assert p.published == datetime.fromisoformat("2017-06-12T17:57:34Z")
    assert p.pdf_url == "http://arxiv.org/pdf/1706.03762v7"


def test_parse_empty_feed() -> None:
    empty = '<feed xmlns="http://www.w3.org/2005/Atom"></feed>'
    assert parse_feed(empty) == []


def test_extract_id_with_v_in_category() -> None:
    assert extract_arxiv_id("http://arxiv.org/abs/solv-int/9901001v1") == ("solv-int/9901001", 1)

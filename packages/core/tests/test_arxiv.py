from datetime import datetime

import pytest

from scholarlens_core.arxiv import extract_arxiv_id, parse_feed


def make_entry(
    arxiv_id: str = "1706.03762",
    version: int = 7,
    title: str = "Attention Is All You Need",
    abstract: str = "The dominant sequence transduction models.",
    authors: list[str] | None = None,
    published: str = "2017-06-12T17:57:34Z",
    has_pdf: bool = True,
) -> str:
    """Buat satu <entry> Atom untuk pengujian. Semua argumen punya nilai bawaan."""
    if authors is None:  # jangan pakai list sebagai default: dipakai bersama semua pemanggilan
        authors = ["Ashish Vaswani", "Noam Shazeer"]
    authors_xml = "".join(f"<author><name>{a}</name></author>" for a in authors)
    pdf_xml = (
        f'<link title="pdf" href="http://arxiv.org/pdf/{arxiv_id}v{version}" '
        'rel="related" type="application/pdf"/>'
        if has_pdf
        else ""
    )
    return f"""<entry>
  <id>http://arxiv.org/abs/{arxiv_id}v{version}</id>
  <published>{published}</published>
  <title>{title}</title>
  <summary>{abstract}</summary>
  {authors_xml}
  <link href="http://arxiv.org/abs/{arxiv_id}v{version}" rel="alternate" type="text/html"/>
  {pdf_xml}
</entry>"""


def make_feed(entries: list[str]) -> str:
    """Bungkus beberapa <entry> menjadi satu umpan Atom."""
    entries_xml = "\n".join(entries)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
{entries_xml}
</feed>"""


@pytest.mark.parametrize(
    "id_url,expected",
    [
        ("http://arxiv.org/abs/1706.03762v7", ("1706.03762", 7)),
        ("http://arxiv.org/abs/hep-th/9901001v1", ("hep-th/9901001", 1)),
        ("http://arxiv.org/abs/solv-int/9901001v1", ("solv-int/9901001", 1)),
    ],
)
def test_extract_arxiv_id(id_url: str, expected: tuple[str, int]) -> None:
    assert extract_arxiv_id(id_url) == expected


def test_parse_feed_basic_fields() -> None:
    xml = make_feed(
        [
            make_entry(
                title="Attention Is All\n  You Need",
                abstract="  The dominant sequence\n transduction models.  ",
            )
        ]
    )
    papers = parse_feed(xml)
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
    assert parse_feed(make_feed([])) == []


def test_entry_without_pdf_link_raises() -> None:
    xml = make_feed([make_entry(has_pdf=False)])
    with pytest.raises(ValueError, match="1706.03762"):
        parse_feed(xml)


@pytest.mark.parametrize(
    "bad_url",
    [
        pytest.param("ngawur", id="no-abs"),
        pytest.param("http://arxiv.org/abs/1706.03762", id="no-version"),
        pytest.param("http://arxiv.org/abs/", id="empty-after-abs"),
        pytest.param("http://arxiv.org/abs/1706.03762vX", id="non-numeric-version"),
    ],
)
def test_bad_url(bad_url: str) -> None:
    with pytest.raises(ValueError, match="Invalid arXiv ID"):
        extract_arxiv_id(bad_url)


def test_parse_feed_multiple_entries() -> None:
    xml = make_feed(
        [
            make_entry(arxiv_id="1706.03762", version=7),
            make_entry(arxiv_id="hep-th/9901001", version=1),
        ]
    )
    papers = parse_feed(xml)
    assert len(papers) == 2
    assert papers[0].arxiv_id == "1706.03762"
    assert papers[0].version == 7
    assert papers[1].arxiv_id == "hep-th/9901001"
    assert papers[1].version == 1

def test_parse_feed_no_authors() -> None:
    xml = make_feed([make_entry(authors=[])])
    papers = parse_feed(xml)
    assert len(papers) == 1
    assert papers[0].authors == []

# value error for empty title because title is required field in arxiv feed and it is an important field for the PaperMeta dataclass. If the title is empty, it indicates that the feed is malformed or incomplete, and it is not possible to create a valid PaperMeta object without a title. Therefore, raising a ValueError in this case is appropriate to signal that there is an issue with the input data.
def test_parse_missing_title() -> None:
    with pytest.raises(ValueError, match="Title not found"):
        xml = make_feed([make_entry(title="")])
        parse_feed(xml)
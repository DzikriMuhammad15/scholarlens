import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime

from scholarlens_core.text import normalize_whitespace


@dataclass(frozen=True)
class PaperMeta:
    arxiv_id: str
    version: int
    title: str
    abstract: str
    authors: list[str]
    published: datetime
    pdf_url: str


ATOM = {"a": "http://www.w3.org/2005/Atom"}


def extract_arxiv_id(id_url: str) -> tuple[str, int]:
    """'http://arxiv.org/abs/1706.03762v7' -> ('1706.03762', 7)"""
    try:
        parts = id_url.split("/abs/")[1]
        arxiv_id, version_str = parts.rsplit("v", maxsplit=1)
        version = int(version_str)
        return arxiv_id, version
    except (IndexError, ValueError):
        raise ValueError(f"Invalid arXiv ID: {id_url}")


def _parse_entry(entry: ET.Element) -> PaperMeta:
    arxiv_id, version = extract_arxiv_id(entry.findtext("a:id", default="", namespaces=ATOM))
    title = normalize_whitespace(entry.findtext("a:title", default="", namespaces=ATOM))
    abstract = normalize_whitespace(entry.findtext("a:summary", default="", namespaces=ATOM))
    authors = [
        normalize_whitespace(author.findtext("a:name", default="", namespaces=ATOM))
        for author in entry.findall("a:author", namespaces=ATOM)
    ]
    published = datetime.fromisoformat(entry.findtext("a:published", default="", namespaces=ATOM))
    pdf_url = None
    for link in entry.findall("a:link", namespaces=ATOM):
        if link.get("title") == "pdf":
            pdf_url = link.get("href")
            break

    if pdf_url is None:
        raise ValueError(f"PDF link not found for {arxiv_id}")
    if not title:
        raise ValueError(f"Title not found for {arxiv_id}")
    
    return PaperMeta(
        arxiv_id=arxiv_id,
        version=version,
        title=title,
        abstract=abstract,
        authors=authors,
        published=published,
        pdf_url=pdf_url,
    )


def parse_feed(xml_text: str) -> list[PaperMeta]:
    """Ubah XML Atom dari arXiv menjadi daftar PaperMeta."""
    root = ET.fromstring(xml_text)
    entries = root.findall("a:entry", ATOM)
    return [_parse_entry(entry) for entry in entries]

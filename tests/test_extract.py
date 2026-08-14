"""Tests contra HTML real descargado de books.toscrape.com (fixtures offline).

Se usan fixtures guardadas en vez de golpear la red en cada corrida de
tests, siguiendo la misma política de cortesía documentada en
/DOCS/onboarding_scraper.md — los tests no deben generar tráfico al sitio.
"""

from tests.conftest import FIXTURES_DIR

from scraper.extract_detail import parse_detail_page
from scraper.extract_listing import has_next_page, parse_listing_page, read_page_indicator


def _read(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


def test_parse_listing_page_extracts_20_cards():
    html = _read("listing_page_1.html")
    records = parse_listing_page(html, "https://books.toscrape.com/catalogue/page-1.html")
    assert len(records) == 20


def test_parse_listing_page_first_card_fields():
    html = _read("listing_page_1.html")
    records = parse_listing_page(html, "https://books.toscrape.com/catalogue/page-1.html")
    first = records[0]
    assert first["title"] == "A Light in the Attic"
    assert first["product_url"].endswith("a-light-in-the-attic_1000/index.html")
    assert first["price_raw"] == "£51.77"
    assert "In stock" in first["availability_raw"]
    assert first["rating_raw"] == "Three"
    assert first["image_url"].startswith("https://books.toscrape.com/")


def test_has_next_page_true_on_page_1():
    html = _read("listing_page_1.html")
    assert has_next_page(html) is True


def test_has_next_page_false_on_last_page():
    html = _read("listing_page_50.html")
    assert has_next_page(html) is False


def test_page_indicator_text():
    html = _read("listing_page_1.html")
    indicator = read_page_indicator(html)
    assert indicator is not None
    assert "1" in indicator and "50" in indicator


def test_parse_detail_page_fields():
    html = _read("detail_a_light_in_the_attic.html")
    url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    data = parse_detail_page(html, url)
    assert data["upc"] == "a897fe39b1053632"
    assert data["price_excl_tax_raw"] == "£51.77"
    assert data["tax_raw"] == "£0.00"
    assert data["availability_detail_raw"] == "In stock (22 available)"
    assert data["reviews_count_raw"] == "0"
    assert data["category"] == "Poetry"
    assert data["description"] and "A Light in the Attic" in data["description"]

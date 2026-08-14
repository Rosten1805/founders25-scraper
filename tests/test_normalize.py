"""Tests unitarios de normalize.py — cubren los 5 casos límite de
/DOCS/data_contract.md §3.
"""

import pytest

from scraper.exceptions import RequiredFieldMissingError
from scraper.normalize import (
    build_record,
    map_rating,
    normalize_availability,
    normalize_price,
    normalize_text,
    parse_stock_count,
)


# --- normalize_price -------------------------------------------------------

@pytest.mark.parametrize(
    "raw, expected",
    [
        ("£51.77", 51.77),
        ("£0.00", 0.0),  # caso límite #2
        ("£1,234.50", 1234.50),
        (None, None),
        ("no price here", None),
    ],
)
def test_normalize_price(raw, expected):
    assert normalize_price(raw) == expected


# --- normalize_availability --------------------------------------------------

@pytest.mark.parametrize(
    "raw, expected",
    [
        ("In stock (22 available)", True),
        ("In stock (0 available)", True),  # caso límite #5: en stock pero 0 unidades
        ("Out of stock", False),  # caso límite #5
        (None, False),
        ("", False),
    ],
)
def test_normalize_availability(raw, expected):
    assert normalize_availability(raw) is expected


def test_parse_stock_count():
    assert parse_stock_count("In stock (22 available)") == 22
    assert parse_stock_count("In stock (0 available)") == 0
    assert parse_stock_count("Out of stock") is None
    assert parse_stock_count(None) is None


# --- map_rating (caso límite #3) --------------------------------------------

def test_map_rating_known_classes():
    assert map_rating("One") == 1
    assert map_rating("Five") == 5


def test_map_rating_unknown_class_returns_none_not_error():
    assert map_rating("Zero") is None
    assert map_rating(None) is None


# --- normalize_text (caso límite #1: caracteres especiales) ------------------

def test_normalize_text_preserves_accents_and_quotes():
    assert normalize_text("Sharp Objects") == "Sharp Objects"
    assert normalize_text("  It's   a   test  ") == "It's a test"
    assert normalize_text("Café Élite") == "Café Élite"
    assert normalize_text(None) is None


# --- build_record (integración de los casos límite) --------------------------

def test_build_record_happy_path():
    listing_raw = {
        "title": "A Light in the Attic",
        "product_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
        "price_raw": "£51.77",
        "availability_raw": "In stock (22 available)",
        "rating_raw": "Three",
        "image_url": "https://books.toscrape.com/media/x.jpg",
    }
    detail_raw = {
        "upc": "a897fe39b1053632",
        "category": "Poetry",
        "price_excl_tax_raw": "£51.77",
        "price_incl_tax_raw": "£51.77",
        "tax_raw": "£0.00",
        "availability_detail_raw": "In stock (22 available)",
        "reviews_count_raw": "0",
        "description": None,  # caso límite #4
    }
    record = build_record(listing_raw, detail_raw)
    assert record.title == "A Light in the Attic"
    assert record.price == 51.77
    assert record.currency == "GBP"
    assert record.rating == 3
    assert record.availability is True
    assert record.stock_count == 22
    assert record.description is None  # no debe fallar por descripción ausente


def test_build_record_missing_title_raises():
    listing_raw = {"title": None, "product_url": "https://x/y", "price_raw": "£1.00"}
    with pytest.raises(RequiredFieldMissingError):
        build_record(listing_raw)


def test_build_record_missing_price_raises():
    listing_raw = {"title": "Book", "product_url": "https://x/y", "price_raw": None}
    with pytest.raises(RequiredFieldMissingError):
        build_record(listing_raw)


def test_build_record_unmapped_rating_does_not_drop_record():
    listing_raw = {
        "title": "Book",
        "product_url": "https://x/y",
        "price_raw": "£1.00",
        "rating_raw": "Zero",  # caso límite #3
    }
    record = build_record(listing_raw)
    assert record.rating is None  # degradado, no descartado

import json
import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import books
from books import BookCollection


@pytest.fixture(autouse=True)
def use_temp_data_file(tmp_path, monkeypatch):
    """Use a temporary data file for each test."""
    temp_file = tmp_path / "data.json"
    temp_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", str(temp_file))


def test_add_book():
    collection = BookCollection()
    initial_count = len(collection.books)
    collection.add_book("1984", "George Orwell", 1949)
    assert len(collection.books) == initial_count + 1
    book = collection.find_book_by_title("1984")
    assert book is not None
    assert book.author == "George Orwell"
    assert book.year == 1949
    assert book.read is False

def test_mark_book_as_read():
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)
    result = collection.mark_as_read("Dune")
    assert result is True
    book = collection.find_book_by_title("Dune")
    assert book.read is True

def test_mark_book_as_read_invalid():
    collection = BookCollection()
    result = collection.mark_as_read("Nonexistent Book")
    assert result is False

def test_remove_book():
    collection = BookCollection()
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    result = collection.remove_book("The Hobbit")
    assert result is True
    book = collection.find_book_by_title("The Hobbit")
    assert book is None

def test_remove_book_invalid():
    collection = BookCollection()
    result = collection.remove_book("Nonexistent Book")
    assert result is False


def test_list_by_year_includes_books_on_both_boundaries() -> None:
    collection = BookCollection()
    first = collection.add_book("First", "Author", 2000)
    middle = collection.add_book("Middle", "Author", 2005)
    last = collection.add_book("Last", "Author", 2010)
    collection.add_book("Earlier", "Author", 1999)
    collection.add_book("Later", "Author", 2011)

    assert collection.list_by_year(2000, 2010) == [first, middle, last]


def test_list_by_year_returns_empty_list_when_no_books_match() -> None:
    collection = BookCollection()
    collection.add_book("A Book", "An Author", 1999)

    assert collection.list_by_year(2000, 2010) == []


def test_list_by_year_rejects_reversed_range() -> None:
    collection = BookCollection()

    with pytest.raises(ValueError, match="Start year cannot be greater than end year"):
        collection.list_by_year(2010, 2000)


def test_missing_data_file_starts_with_empty_collection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(books, "DATA_FILE", str(tmp_path / "missing.json"))

    collection = BookCollection()

    assert collection.list_books() == []


def test_load_books_restores_valid_records(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    data_file = tmp_path / "books.json"
    data_file.write_text(
        '[{"title": "Dune", "author": "Frank Herbert", '
        '"year": 1965, "read": true}]'
    )
    monkeypatch.setattr(books, "DATA_FILE", str(data_file))

    collection = BookCollection()

    assert collection.list_books() == [
        books.Book("Dune", "Frank Herbert", 1965, read=True)
    ]


@pytest.mark.parametrize(
    "content",
    [
        "{invalid json",
        '{"title": "Dune"}',
        '[{"unexpected": "field"}]',
        '[{"title": null, "author": "Frank Herbert", "year": 1965}]',
        '[{"title": "Dune", "author": "Frank Herbert", "year": "1965"}]',
    ],
)
def test_load_books_rejects_invalid_data_without_changing_source(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    content: str,
) -> None:
    data_file = tmp_path / "books.json"
    data_file.write_text(content)
    monkeypatch.setattr(books, "DATA_FILE", str(data_file))

    with pytest.raises(ValueError, match="Invalid book data"):
        BookCollection()

    assert data_file.read_text() == content


def test_save_books_writes_indented_json_and_can_be_reloaded(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    data_file = tmp_path / "books.json"
    data_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", str(data_file))
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)

    saved_text = data_file.read_text()
    reloaded_collection = BookCollection()

    assert "  \"title\": \"Dune\"" in saved_text
    assert json.loads(saved_text) == [
        {"title": "Dune", "author": "Frank Herbert", "year": 1965, "read": False}
    ]
    assert reloaded_collection.list_books() == collection.list_books()


def test_save_books_preserves_original_file_if_replace_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    data_file = tmp_path / "books.json"
    data_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", str(data_file))
    collection = BookCollection()

    def fail_replace(source: str, destination: str) -> None:
        raise OSError("replace failed")

    monkeypatch.setattr(books.os, "replace", fail_replace)
    with pytest.raises(OSError, match="replace failed"):
        collection.add_book("Dune", "Frank Herbert", 1965)

    assert data_file.read_text() == "[]"
    assert sorted(path.name for path in tmp_path.iterdir()) == [
        "books.json",
        "data.json",
    ]


def test_find_book_by_title_is_case_insensitive_and_returns_none_when_missing() -> None:
    collection = BookCollection()
    book = collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)

    assert collection.find_book_by_title("tHe HoBbIt") is book
    assert collection.find_book_by_title("Dune") is None


def test_find_by_author_matches_full_name_ignoring_case() -> None:
    collection = BookCollection()
    first = collection.add_book("Dune", "Frank Herbert", 1965)
    second = collection.add_book("Children of Dune", "Frank Herbert", 1976)
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)

    assert collection.find_by_author("FRANK HERBERT") == [first, second]
    assert collection.find_by_author("Frank") == []


def test_search_books_finds_partial_matches_in_title_and_author() -> None:
    collection = BookCollection()
    title_match = collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    author_match = collection.add_book("The Silmarillion", "J.R.R. Tolkien", 1977)

    assert collection.search_books("HOB") == [title_match]
    assert collection.search_books("tolkien") == [title_match, author_match]


def test_search_books_casefolds_query_and_rejects_blank_query() -> None:
    collection = BookCollection()
    book = collection.add_book("The Straße", "A. Writer", 2020)

    assert collection.search_books("STRASSE") == [book]
    with pytest.raises(ValueError, match="Search query cannot be empty"):
        collection.search_books("  ")


def test_list_books_returns_the_collection_list() -> None:
    collection = BookCollection()

    assert collection.list_books() is collection.books

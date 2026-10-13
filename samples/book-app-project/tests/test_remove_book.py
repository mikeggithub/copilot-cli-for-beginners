import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import books
from books import BookCollection


@pytest.fixture
def collection(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> BookCollection:
    data_file = tmp_path / "data.json"
    data_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", str(data_file))
    return BookCollection()


def test_remove_book_removes_exact_matching_title(
    collection: BookCollection,
) -> None:
    dune = collection.add_book("Dune", "Frank Herbert", 1965)
    dune_messiah = collection.add_book("Dune Messiah", "Frank Herbert", 1969)

    assert collection.remove_book("Dune") is True
    assert collection.list_books() == [dune_messiah]
    assert dune not in collection.list_books()


def test_remove_book_matches_title_case_insensitively(
    collection: BookCollection,
) -> None:
    book = collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)

    assert collection.remove_book("  tHe HoBbIt  ") is True
    assert collection.list_books() == []
    assert book not in collection.list_books()


def test_remove_book_returns_false_when_title_is_not_found(
    collection: BookCollection,
) -> None:
    book = collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)

    assert collection.remove_book("Dune") is False
    assert collection.list_books() == [book]


def test_remove_book_can_remove_book_with_blank_title(
    collection: BookCollection,
) -> None:
    collection.add_book("", "Unknown", 0)

    assert collection.remove_book("   ") is True
    assert collection.list_books() == []


def test_remove_book_returns_false_for_empty_collection(
    collection: BookCollection,
) -> None:
    assert collection.remove_book("Dune") is False
    assert collection.list_books() == []

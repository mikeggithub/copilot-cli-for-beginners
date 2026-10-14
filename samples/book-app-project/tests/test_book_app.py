import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import book_app
import books
from books import BookCollection


@pytest.fixture
def collection(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> BookCollection:
    data_file = tmp_path / "data.json"
    data_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", str(data_file))
    return BookCollection()


def test_handle_add_rejects_empty_title(
    collection: BookCollection,
    capsys: pytest.CaptureFixture[str],
) -> None:
    with patch("builtins.input", side_effect=["", "An Author", "2000"]):
        book_app.handle_add(collection)

    assert collection.list_books() == []
    assert "title and author cannot be empty" in capsys.readouterr().out


def test_handle_add_rejects_invalid_year(
    collection: BookCollection,
    capsys: pytest.CaptureFixture[str],
) -> None:
    with patch("builtins.input", side_effect=["A Book", "An Author", "unknown"]):
        book_app.handle_add(collection)

    assert collection.list_books() == []
    assert "whole number for the year" in capsys.readouterr().out


def test_search_books_matches_partial_title_case_insensitively(
    collection: BookCollection,
) -> None:
    book = collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)

    assert collection.search_books("HOB") == [book]


def test_search_books_matches_partial_author_case_insensitively(
    collection: BookCollection,
) -> None:
    book = collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)

    assert collection.search_books("tolkien") == [book]


def test_search_books_returns_no_results_for_unmatched_query(
    collection: BookCollection,
) -> None:
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)

    assert collection.search_books("Dune") == []


def test_search_books_rejects_empty_query(collection: BookCollection) -> None:
    with pytest.raises(ValueError, match="Search query cannot be empty"):
        collection.search_books("  ")


def test_handle_find_searches_by_title_or_author(
    collection: BookCollection,
    capsys: pytest.CaptureFixture[str],
) -> None:
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    with patch("builtins.input", return_value="hob"):
        book_app.handle_find(collection)

    assert "The Hobbit by J.R.R. Tolkien" in capsys.readouterr().out


def test_handle_find_rejects_empty_search_term(
    collection: BookCollection,
    capsys: pytest.CaptureFixture[str],
) -> None:
    with patch("builtins.input", return_value="  "):
        book_app.handle_find(collection)

    assert "search term cannot be empty" in capsys.readouterr().out


def test_main_list_unread_shows_only_unread_books(
    collection: BookCollection,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    collection.add_book("1984", "George Orwell", 1949)
    collection.mark_as_read("1984")
    monkeypatch.setattr(book_app.sys, "argv", ["book_app.py", "list", "unread"])

    book_app.main()
    output = capsys.readouterr().out

    assert "The Hobbit by J.R.R. Tolkien" in output
    assert "1984 by George Orwell" not in output


def test_main_list_unread_reports_when_no_unread_books_exist(
    collection: BookCollection,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    collection.add_book("1984", "George Orwell", 1949)
    collection.mark_as_read("1984")
    monkeypatch.setattr(book_app.sys, "argv", ["book_app.py", "list", "unread"])

    book_app.main()

    assert "No books found." in capsys.readouterr().out


def test_main_list_unread_command_is_case_insensitive(
    collection: BookCollection,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    monkeypatch.setattr(book_app.sys, "argv", ["book_app.py", "LIST", "UNREAD"])

    book_app.main()

    assert "The Hobbit by J.R.R. Tolkien" in capsys.readouterr().out


def test_main_list_still_shows_read_and_unread_books(
    collection: BookCollection,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    collection.add_book("1984", "George Orwell", 1949)
    collection.mark_as_read("1984")
    monkeypatch.setattr(book_app.sys, "argv", ["book_app.py", "list"])

    book_app.main()
    output = capsys.readouterr().out

    assert "The Hobbit by J.R.R. Tolkien" in output
    assert "1984 by George Orwell" in output


def test_help_lists_list_unread_command(capsys: pytest.CaptureFixture[str]) -> None:
    book_app.display.show_help()

    assert "list unread" in capsys.readouterr().out


def test_main_reports_data_file_error(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fail_to_load() -> BookCollection:
        raise PermissionError("permission denied")

    monkeypatch.setattr(book_app.sys, "argv", ["book_app.py", "list"])
    monkeypatch.setattr(book_app, "BookCollection", fail_to_load)

    book_app.main()

    assert "Could not access the book data file" in capsys.readouterr().err


def test_main_reports_invalid_book_data(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fail_to_load() -> BookCollection:
        raise ValueError("invalid record 1")

    monkeypatch.setattr(book_app.sys, "argv", ["book_app.py", "list"])
    monkeypatch.setattr(book_app, "BookCollection", fail_to_load)

    book_app.main()

    assert (
        "Could not load the book data file: invalid record 1"
        in capsys.readouterr().err
    )


def test_main_handles_end_of_input(
    collection: BookCollection,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(book_app.sys, "argv", ["book_app.py", "add"])
    with patch("builtins.input", side_effect=EOFError):
        book_app.main()

    assert "Operation cancelled" in capsys.readouterr().err


def test_load_books_rejects_invalid_json_structure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    data_file = tmp_path / "data.json"
    data_file.write_text('{"not": "a list"}')
    monkeypatch.setattr(books, "DATA_FILE", str(data_file))

    with pytest.raises(ValueError, match="expected a list of books"):
        BookCollection()

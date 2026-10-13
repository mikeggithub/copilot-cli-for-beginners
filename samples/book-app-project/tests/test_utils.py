import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import utils
import display
from books import Book


def test_get_user_choice_reprompts_for_empty_and_non_numeric_input(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with patch("builtins.input", side_effect=["  ", "abc", "3"]):
        choice = utils.get_user_choice()

    assert choice == "3"
    output = capsys.readouterr().out
    assert "Please enter a choice." in output
    assert "Please enter a number." in output


def test_get_user_choice_reprompts_for_numbers_outside_range(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with patch("builtins.input", side_effect=["0", "6", "3"]):
        assert utils.get_user_choice() == "3"

    assert "Please choose a number from 1 to 5." in capsys.readouterr().out


def test_get_user_choice_returns_numeric_input() -> None:
    with patch("builtins.input", return_value=" 2 "):
        assert utils.get_user_choice() == "2"


def test_get_book_details_reprompts_for_empty_title(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with patch(
        "builtins.input",
        side_effect=["  ", "The Hobbit", "J.R.R. Tolkien", "1937"],
    ):
        details = utils.get_book_details()

    assert details == ("The Hobbit", "J.R.R. Tolkien", 1937)
    assert "Book title cannot be empty." in capsys.readouterr().out


def test_get_book_details_reprompts_for_invalid_year(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with patch(
        "builtins.input",
        side_effect=["The Hobbit", "J.R.R. Tolkien", "unknown", "1937"],
    ):
        details = utils.get_book_details()

    assert details == ("The Hobbit", "J.R.R. Tolkien", 1937)
    assert "Invalid year. Please enter a whole number." in capsys.readouterr().out


def test_print_books_displays_collection(capsys: pytest.CaptureFixture[str]) -> None:
    display.print_books([Book("The Hobbit", "J.R.R. Tolkien", 1937, read=True)])

    output = capsys.readouterr().out
    assert "Your Book Collection" in output
    assert "[✓] The Hobbit by J.R.R. Tolkien (1937)" in output


def test_print_books_reports_empty_collection(
    capsys: pytest.CaptureFixture[str],
) -> None:
    display.print_books([])

    assert capsys.readouterr().out.strip() == "No books found."

import sys

from books import Book


def show_message(message: str) -> None:
    print(message)


def show_error(message: str) -> None:
    print(message, file=sys.stderr)


def print_menu() -> None:
    print("\n📚 Book Collection App")
    print("1. Add a book")
    print("2. List books")
    print("3. Mark book as read")
    print("4. Remove a book")
    print("5. Exit")


def print_books(books: list[Book]) -> None:
    """Display books in a user-friendly format."""
    if not books:
        show_message("No books found.")
        return

    print("\nYour Book Collection:\n")
    for index, book in enumerate(books, start=1):
        status = "✓" if book.read else " "
        print(f"{index}. [{status}] {book.title} by {book.author} ({book.year})")

    print()


def show_help() -> None:
    show_message(
        """
Book Collection Helper

Commands:
  list     - Show all books
  add      - Add a new book
  remove   - Remove a book by title
  find     - Find books by title or author
  help     - Show this help message
"""
    )

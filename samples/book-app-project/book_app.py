import sys
from collections.abc import Callable

from books import BookCollection
import display


def handle_list(book_collection: BookCollection) -> None:
    books = book_collection.list_books()
    display.print_books(books)


def handle_add(book_collection: BookCollection) -> None:
    display.show_message("\nAdd a New Book\n")

    title = input("Title: ").strip()
    author = input("Author: ").strip()
    year_str = input("Year: ").strip()

    if not title or not author:
        display.show_message("\nError: title and author cannot be empty.\n")
        return

    try:
        year = int(year_str) if year_str else 0
    except ValueError:
        display.show_message(
            "\nError: enter a whole number for the year, or leave it blank.\n"
        )
        return

    book_collection.add_book(title, author, year)
    display.show_message("\nBook added successfully.\n")


def handle_remove(book_collection: BookCollection) -> None:
    display.show_message("\nRemove a Book\n")

    title = input("Enter the title of the book to remove: ").strip()
    if not title:
        display.show_message("\nError: title cannot be empty.\n")
        return

    if book_collection.remove_book(title):
        display.show_message("\nBook removed successfully.\n")
    else:
        display.show_message("\nNo book with that title was found.\n")


def handle_find(book_collection: BookCollection) -> None:
    display.show_message("\nFind Books by Title or Author\n")

    query = input("Search by title or author: ").strip()
    if not query:
        display.show_message("\nError: search term cannot be empty.\n")
        return

    books = book_collection.search_books(query)

    display.print_books(books)


def main() -> None:
    if len(sys.argv) < 2:
        display.show_help()
        return

    command = sys.argv[1].lower()

    if command == "help":
        display.show_help()
        return

    handlers: dict[str, Callable[[BookCollection], None]] = {
        "list": handle_list,
        "add": handle_add,
        "remove": handle_remove,
        "find": handle_find,
    }
    handler = handlers.get(command)
    if handler is None:
        display.show_message("Unknown command.\n")
        display.show_help()
        return

    try:
        book_collection = BookCollection()
    except OSError as error:
        display.show_error(f"\nCould not access the book data file: {error}\n")
        return
    except ValueError as error:
        display.show_error(f"\nCould not load the book data file: {error}\n")
        return

    try:
        handler(book_collection)
    except (EOFError, KeyboardInterrupt):
        display.show_error("\nOperation cancelled.\n")
    except OSError as error:
        display.show_error(f"\nCould not access the book data file: {error}\n")


if __name__ == "__main__":
    main()

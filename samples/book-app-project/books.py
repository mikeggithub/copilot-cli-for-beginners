"""Manage a book collection and save it as JSON in ``data.json``.

The :class:`Book` dataclass represents one book. Use :class:`BookCollection`
to load, search, update, and save books.
"""

import json
import os
import tempfile
from dataclasses import dataclass, asdict
from typing import List, Optional

DATA_FILE = "data.json"


@dataclass
class Book:
    """A book's details and reading status.

    Attributes:
        title (str): The book's title.
        author (str): The name of the book's author.
        year (int): The book's publication year.
        read (bool): Whether the book has been read; defaults to ``False``.

    Example:
        >>> book = Book("Dune", "Frank Herbert", 1965)
        >>> book.read
        False
    """

    title: str
    author: str
    year: int
    read: bool = False


class BookCollection:
    """Store books and persist collection changes to the JSON data file.

    A missing data file starts as an empty collection. Add, mark-as-read, and
    remove operations save their changes automatically; searches and listing
    operations only read the in-memory collection.

    Example:
        >>> collection = BookCollection()
        >>> collection.add_book("Dune", "Frank Herbert", 1965)
        Book(title='Dune', author='Frank Herbert', year=1965, read=False)
    """

    def __init__(self) -> None:
        """Create a collection and load its books from ``DATA_FILE``.

        If the file is missing, the collection starts empty. Invalid JSON,
        an invalid collection schema, or invalid book field types raise
        ``ValueError``; invalid data is not silently replaced with an empty
        collection.

        Returns:
            None.

        Raises:
            OSError: If the data file cannot be opened or read.
            ValueError: If the file contains malformed JSON, is not a list of
                book objects, or contains missing/extra fields or field
                values with invalid types. A book must have ``title`` and
                ``author`` strings, an integer ``year`` (not a boolean), and
                an optional boolean ``read``.

        Example:
            >>> collection = BookCollection()
            >>> isinstance(collection.list_books(), list)
            True
        """
        self.books: List[Book] = []
        self.load_books()

    def load_books(self) -> None:
        """Load books from the JSON file if it exists.

        A missing file sets the collection to empty. Otherwise the file must
        contain a JSON list of objects matching the ``Book`` fields:
        ``title`` and ``author`` must be strings, ``year`` must be an integer
        (not a boolean), and ``read``, if present, must be a boolean. Missing
        or extra fields, invalid field types, and malformed JSON raise
        ``ValueError`` rather than silently discarding the data. Books are
        replaced in memory only after the complete file has been validated.

        Returns:
            None.

        Raises:
            OSError: If the file cannot be opened or read.
            ValueError: If the JSON is malformed, the top-level value is not
                a list, a record is not an object, or a record has invalid
                fields or field types.

        Example:
            >>> collection = BookCollection()
            >>> collection.load_books()
        """
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            self.books = []
            return
        except json.JSONDecodeError as error:
            raise ValueError(
                f"Invalid book data in {DATA_FILE}: {error}"
            ) from error

        try:
            if not isinstance(data, list):
                raise ValueError("expected a list of books")

            loaded_books = []
            for index, record in enumerate(data, start=1):
                if not isinstance(record, dict):
                    raise ValueError(f"record {index} must be an object")
                try:
                    book = Book(**record)
                except TypeError as error:
                    raise ValueError(f"record {index}: {error}") from error
                if (
                    not isinstance(book.title, str)
                    or not isinstance(book.author, str)
                    or type(book.year) is not int
                    or type(book.read) is not bool
                ):
                    raise ValueError(f"record {index} has invalid field types")
                loaded_books.append(book)
        except (TypeError, ValueError) as error:
            raise ValueError(f"Invalid book data in {DATA_FILE}: {error}") from error

        self.books = loaded_books

    def save_books(self) -> None:
        """Save the current books to ``DATA_FILE`` as formatted JSON.

        JSON serialization completes before any file is written. The
        serialized data is written to a temporary file in the destination
        directory, then replaces ``DATA_FILE`` with ``os.replace``; this
        avoids exposing a partially written data file. Serialization errors
        therefore leave the existing data file untouched. The replacement
        is atomic when supported by the underlying filesystem, but this
        method does not guarantee durability across a power loss.

        Returns:
            None.

        Raises:
            OSError: If creating or writing the temporary file, replacing
                ``DATA_FILE``, or related filesystem operations fail.
            TypeError: If a book contains a value that cannot be serialized
                as JSON. This occurs before the filesystem is modified.

        Example:
            >>> collection = BookCollection()
            >>> collection.save_books()
        """
        serialized = json.dumps([asdict(book) for book in self.books], indent=2)
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=os.path.dirname(os.path.abspath(DATA_FILE)),
                delete=False,
            ) as temporary_file:
                temporary_path = temporary_file.name
                temporary_file.write(serialized)
                temporary_file.write("\n")
            os.replace(temporary_path, DATA_FILE)
        except OSError:
            if temporary_path is not None:
                try:
                    os.unlink(temporary_path)
                except FileNotFoundError:
                    pass
            raise

    def add_book(self, title: str, author: str, year: int) -> Book:
        """Add a book and save the updated collection.

        Args:
            title (str): The book's title.
            author (str): The book's author.
            year (int): The book's publication year.

        Returns:
            Book: The newly created book.

        Raises:
            OSError: If the updated collection cannot be saved.
            TypeError: If the book's values cannot be serialized as JSON.

        Example:
            >>> collection = BookCollection()
            >>> book = collection.add_book("Dune", "Frank Herbert", 1965)
            >>> book.title
            'Dune'
        """
        book = Book(title=title, author=author, year=year)
        self.books.append(book)
        self.save_books()
        return book

    def list_books(self) -> List[Book]:
        """Return the collection's books.

        Returns:
            List[Book]: The mutable list of books held by this collection.

        Example:
            >>> collection = BookCollection()
            >>> books = collection.list_books()
            >>> all(isinstance(book, Book) for book in books)
            True
        """
        return self.books

    def list_by_year(self, start: int, end: int) -> List[Book]:
        """Return books published within an inclusive year range.

        Args:
            start (int): The earliest publication year to include.
            end (int): The latest publication year to include.

        Returns:
            List[Book]: Books whose publication years are between ``start``
                and ``end``, including both boundaries.

        Raises:
            ValueError: If ``start`` is greater than ``end``.

        Example:
            >>> collection = BookCollection()
            >>> collection.list_by_year(1900, 2000)
            []
        """
        if start > end:
            raise ValueError("Start year cannot be greater than end year.")

        return [book for book in self.books if start <= book.year <= end]

    def find_book_by_title(self, title: str) -> Optional[Book]:
        """Find the first book whose title matches, ignoring case.

        Args:
            title (str): The title to look up.

        Returns:
            Optional[Book]: The matching book, or ``None`` if not found.

        Example:
            >>> collection = BookCollection()
            >>> collection.find_book_by_title("Dune") is None
            True
        """
        for book in self.books:
            if book.title.lower() == title.lower():
                return book
        return None

    def mark_as_read(self, title: str) -> bool:
        """Mark a matching book as read and save the collection.

        Args:
            title (str): The title of the book to mark as read.

        Returns:
            bool: ``True`` if a book was found and marked; otherwise ``False``.

        Raises:
            OSError: If the updated collection cannot be saved.
            TypeError: If a book's values cannot be serialized as JSON.

        Example:
            >>> collection = BookCollection()
            >>> collection.add_book("Dune", "Frank Herbert", 1965)
            Book(title='Dune', author='Frank Herbert', year=1965, read=False)
            >>> collection.mark_as_read("Dune")
            True
        """
        book = self.find_book_by_title(title)
        if book:
            book.read = True
            self.save_books()
            return True
        return False

    def remove_book(self, title: str) -> bool:
        """Remove the first exact title match, ignoring case and outer spaces.

        Args:
            title (str): The title of the book to remove.

        Returns:
            bool: ``True`` if a matching book was removed, or ``False`` if no
                book matches. Callers can use ``False`` to tell the user that
                no book was found. A blank title matches a blank-title book.

        Raises:
            OSError: If the updated collection cannot be saved.
            TypeError: If a book's values cannot be serialized as JSON.

        Example:
            >>> collection = BookCollection()
            >>> collection.add_book("Dune", "Frank Herbert", 1965)
            Book(title='Dune', author='Frank Herbert', year=1965, read=False)
            >>> collection.remove_book("Dune")
            True
        """
        normalized_title = title.strip().casefold()
        for book in self.books:
            if book.title.casefold() == normalized_title:
                self.books.remove(book)
                self.save_books()
                return True
        return False

    def find_by_author(self, author: str) -> List[Book]:
        """Find books by an exact author name, ignoring case.

        Args:
            author (str): The author name to match.

        Returns:
            List[Book]: All books whose author matches ``author``.

        Example:
            >>> collection = BookCollection()
            >>> collection.find_by_author("Frank Herbert")
            []
        """
        return [b for b in self.books if b.author.lower() == author.lower()]

    def search_books(self, query: str) -> List[Book]:
        """Find books with a partial, case-insensitive title or author match.

        Args:
            query (str): The text to search for in titles and author names.

        Returns:
            List[Book]: Books whose title or author contains ``query``.

        Raises:
            ValueError: If ``query`` is empty or contains only whitespace.

        Example:
            >>> collection = BookCollection()
            >>> collection.search_books("dune")
            []
        """
        normalized_query = query.strip().casefold()
        if not normalized_query:
            raise ValueError("Search query cannot be empty.")

        return [
            book
            for book in self.books
            if normalized_query in book.title.casefold()
            or normalized_query in book.author.casefold()
        ]

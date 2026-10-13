import json
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
    def __init__(self) -> None:
        """Create a collection and load its books from ``DATA_FILE``.

        A missing file is treated as an empty collection. Invalid JSON or
        invalid record structures produce a warning and also start empty.

        Returns:
            None.

        Raises:
            OSError: If the data file exists but cannot be opened or read.

        Example:
            >>> collection = BookCollection()
            >>> isinstance(collection.list_books(), list)
            True
        """
        self.books: List[Book] = []
        self.load_books()

    def load_books(self) -> None:
        """Load books from the JSON file if it exists.

        A missing file results in an empty collection. Malformed JSON or
        records that cannot be used to construct ``Book`` objects produce a
        warning and an empty collection.

        Returns:
            None.

        Raises:
            OSError: If the file cannot be opened or read.

        Example:
            >>> collection = BookCollection()
            >>> collection.load_books()
        """
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    raise ValueError("expected a list of books")
                self.books = [Book(**b) for b in data]
        except FileNotFoundError:
            self.books = []
        except (json.JSONDecodeError, TypeError, ValueError) as error:
            print(
                f"Warning: {DATA_FILE} is invalid ({error}). "
                "Starting with an empty collection."
            )
            self.books = []

    def save_books(self) -> None:
        """Write the current books to ``DATA_FILE`` as formatted JSON.

        Returns:
            None.

        Raises:
            OSError: If the file cannot be opened or written.
            TypeError: If a book contains a value that cannot be serialized
                as JSON.

        Example:
            >>> collection = BookCollection()
            >>> collection.save_books()
        """
        with open(DATA_FILE, "w") as f:
            json.dump([asdict(b) for b in self.books], f, indent=2)

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

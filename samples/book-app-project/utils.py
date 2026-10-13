import display


def get_user_choice() -> str:
    while True:
        choice = input("Choose an option (1-5): ").strip()
        if not choice:
            display.show_message("Please enter a choice.")
        elif not choice.isdigit():
            display.show_message("Please enter a number.")
        elif choice not in {"1", "2", "3", "4", "5"}:
            display.show_message("Please choose a number from 1 to 5.")
        else:
            return choice


def get_book_details() -> tuple[str, str, int]:
    """Prompt for a book's title, author, and publication year.

    This function takes no parameters. It repeats the title prompt until a
    non-empty title is entered. If the publication year is not a valid
    integer, it displays a message and prompts again. A year of ``0`` can
    represent an unknown publication year.

    Returns:
        A tuple containing the stripped title, stripped author, and
        publication year as an integer.
    """
    title = ""
    while not title:
        title = input("Enter book title: ").strip()
        if not title:
            display.show_message("Book title cannot be empty.")

    author = input("Enter author: ").strip()

    while True:
        year_input = input("Enter publication year: ").strip()
        try:
            year = int(year_input)
            break
        except ValueError:
            display.show_message("Invalid year. Please enter a whole number.")

    return title, author, year

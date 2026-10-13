import display


def get_user_choice() -> str:
    while True:
        choice = input("Choose an option (1-5): ").strip()
        if not choice:
            display.show_message("Please enter a choice.")
        elif not choice.isdigit():
            display.show_message("Please enter a number.")
        else:
            return choice


def get_book_details() -> tuple[str, str, int]:
    """Prompt for a book's title, author, and publication year.

    This function takes no parameters. It repeats the title prompt until a
    non-empty title is entered. If the publication year is not a valid
    integer, it displays a message and uses ``0``.

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

    year_input = input("Enter publication year: ").strip()
    try:
        year = int(year_input)
    except ValueError:
        display.show_message("Invalid year. Defaulting to 0.")
        year = 0

    return title, author, year

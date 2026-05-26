#!/usr/bin/env python3
"""
Seed the library with sample books across all required genres.

The script uses BookService instead of writing repositories directly so every
created book is captured in the encrypted audit log and can be recovered.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.config import get_settings
from app.models.book import BookCreate, BookType
from app.services.book_service import BookService


SAMPLE_BOOKS = [
    ("The Name of the Wind", "Patrick Rothfuss", BookType.FANTASY, 5),
    ("A Game of Thrones", "George R.R. Martin", BookType.FANTASY, 8),
    ("The Way of Kings", "Brandon Sanderson", BookType.FANTASY, 4),
    ("The Hobbit", "J.R.R. Tolkien", BookType.FANTASY, 6),
    ("Mistborn", "Brandon Sanderson", BookType.FANTASY, 5),
    ("The House in the Cerulean Sea", "TJ Klune", BookType.FANTASY, 3),
    ("Fourth Wing", "Rebecca Yarros", BookType.FANTASY, 7),
    ("Six of Crows", "Leigh Bardugo", BookType.FANTASY, 4),
    ("The Girl with the Dragon Tattoo", "Stieg Larsson", BookType.CRIMINAL, 5),
    ("A Good Girl's Guide to Murder", "Holly Jackson", BookType.CRIMINAL, 6),
    ("The Thursday Murder Club", "Richard Osman", BookType.CRIMINAL, 8),
    ("In Cold Blood", "Truman Capote", BookType.CRIMINAL, 3),
    ("Gone Girl", "Gillian Flynn", BookType.CRIMINAL, 9),
    ("The Girl on the Train", "Paula Hawkins", BookType.CRIMINAL, 7),
    ("Verity", "Colleen Hoover", BookType.CRIMINAL, 5),
    ("The Midnight Library", "Matt Haig", BookType.DRAMA, 10),
    ("Lessons in Chemistry", "Bonnie Garmus", BookType.DRAMA, 6),
    ("Tomorrow, and Tomorrow, and Tomorrow", "Gabrielle Zevin", BookType.DRAMA, 4),
    ("Happy Place", "Emily Henry", BookType.DRAMA, 5),
    ("Daisy Jones & The Six", "Taylor Jenkins Reid", BookType.DRAMA, 7),
    ("The Seven Husbands of Evelyn Hugo", "Taylor Jenkins Reid", BookType.DRAMA, 8),
    ("Carrie", "Stephen King", BookType.DRAMA, 4),
]


def seed_books() -> None:
    get_settings().ensure_data_dir()
    service = BookService()
    existing_keys = {
        (book.title.casefold(), book.author.casefold(), book.book_type)
        for book in service.list_all()
    }

    print(f"Seeding {len(SAMPLE_BOOKS)} books...")
    created_count = 0
    skipped_count = 0
    for title, author, book_type, total_qty in SAMPLE_BOOKS:
        key = (title.casefold(), author.casefold(), book_type)
        if key in existing_keys:
            skipped_count += 1
            print(f"  skipped {title} ({book_type.value}) - already present")
            continue

        book = service.create(
            BookCreate(
                title=title,
                author=author,
                book_type=book_type,
                total_qty=total_qty,
                available_qty=total_qty,
            ),
            actor_id="system",
        )
        existing_keys.add(key)
        created_count += 1
        print(f"  created {book.title} ({book.book_type.value}) - {book.total_qty} copies")

    print(f"\nCreated {created_count} books, skipped {skipped_count} existing books.")
    print(f"Total books in library: {len(service.list_all())}")


if __name__ == "__main__":
    seed_books()

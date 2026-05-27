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
    ("The Name of the Wind", "Patrick Rothfuss", BookType.FANTASY, 5, "https://m.media-amazon.com/images/I/91kBQf9rfqL._UF1000,1000_QL80_.jpg"),
    ("A Game of Thrones", "George R.R. Martin", BookType.FANTASY, 8, "https://m.media-amazon.com/images/M/MV5BMTNhMDJmNmYtNDQ5OS00ODdlLWE0ZDAtZTgyYTIwNDY3OTU3XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"),
    ("The Way of Kings", "Brandon Sanderson", BookType.FANTASY, 4, "https://mpd-biblio-covers.imgix.net/9780765326355.jpg"),
    ("The Hobbit", "J.R.R. Tolkien", BookType.FANTASY, 6, "https://m.media-amazon.com/images/I/81uEDUfKBZL._AC_UF894,1000_QL80_.jpg"),
    ("Mistborn", "Brandon Sanderson", BookType.FANTASY, 5, "https://content2.rozetka.com.ua/goods/images/big/424438196.jpg"),
    ("The House in the Cerulean Sea", "TJ Klune", BookType.FANTASY, 3, "https://m.media-amazon.com/images/I/81MnY8Q7OLL._AC_UF1000,1000_QL80_.jpg"),
    ("Fourth Wing", "Rebecca Yarros", BookType.FANTASY, 7, "https://content1.rozetka.com.ua/goods/images/big/424442472.jpg"),
    ("Six of Crows", "Leigh Bardugo", BookType.FANTASY, 4, "https://www.britishbook.ua/upload/resize_cache/iblock/8a8/0v5rbue6dq2a8v3g121esrpfal162xah/1900_800_174b5ed2089e1946312e2a80dcd26f146/knyga_six_of_crows_book_1.jpg"),
    ("The Girl with the Dragon Tattoo", "Stieg Larsson", BookType.CRIMINAL, 5, "https://m.media-amazon.com/images/M/MV5BMTczNDk4NTQ0OV5BMl5BanBnXkFtZTcwNDAxMDgxNw@@._V1_.jpg"),
    ("A Good Girl's Guide to Murder", "Holly Jackson", BookType.CRIMINAL, 6, "covers/a_good_girl's_guide_to_murder.jpg"),
    ("The Thursday Murder Club", "Richard Osman", BookType.CRIMINAL, 8, "covers/the_thursday_murder_club.jpg"),
    ("In Cold Blood", "Truman Capote", BookType.CRIMINAL, 3, "covers/in_cold_blood.jpg"),
    ("Gone Girl", "Gillian Flynn", BookType.CRIMINAL, 9, "covers/gone_girl.jpg"),
    ("The Girl on the Train", "Paula Hawkins", BookType.CRIMINAL, 7, "covers/the_girl_on_the_train.jpg"),
    ("Verity", "Colleen Hoover", BookType.CRIMINAL, 5, "covers/verity.jpg"),
    ("The Midnight Library", "Matt Haig", BookType.DRAMA, 10, "covers/the_midnight_library.jpg"),
    ("Lessons in Chemistry", "Bonnie Garmus", BookType.DRAMA, 6, "covers/lessons_in_chemistry.jpg"),
    ("Tomorrow, and Tomorrow, and Tomorrow", "Gabrielle Zevin", BookType.DRAMA, 4, "covers/tomorrow_and_tomorrow_and_tomorrow.jpg"),
    ("Happy Place", "Emily Henry", BookType.DRAMA, 5, "covers/happy_place.jpg"),
    ("Daisy Jones & The Six", "Taylor Jenkins Reid", BookType.DRAMA, 7, "covers/daisy_jones_&_the_six.jpg"),
    ("The Seven Husbands of Evelyn Hugo", "Taylor Jenkins Reid", BookType.DRAMA, 8, "covers/the_seven_husbands_of_evelyn_hugo.jpg"),
    ("Carrie", "Stephen King", BookType.DRAMA, 4, "covers/carrie.jpg"),
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

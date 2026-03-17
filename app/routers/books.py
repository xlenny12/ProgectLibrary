from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_current_user, require_role
from app.models.book import BookCreate, BookPublic, BookUpdate
from app.models.user import UserInDB, Role
from app.services.book_service import BookService

router = APIRouter(prefix="/api/books", tags=["books"])


@router.get("", response_model=list[BookPublic])
def list_books(_: UserInDB = Depends(get_current_user)):
    """List all books in the catalog.
    
    Requires authentication. Any authenticated user can view books.
    
    Returns: List of all books with ID, title, author, type, and quantities
    """
    return BookService().list_all()


@router.get("/{book_id}", response_model=BookPublic)
def get_book(book_id: str, _: UserInDB = Depends(get_current_user)):
    """Get details of a specific book.
    
    Requires authentication.
    
    Args: book_id - UUID of the book
    Returns: Book details or 404 if not found
    """
    try:
        return BookService().get(book_id)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.post("", response_model=BookPublic, status_code=status.HTTP_201_CREATED)
def create_book(data: BookCreate, current_user: UserInDB = Depends(require_role(Role.ADMIN))):
    """Add a new book to the catalog.
    
    Admin only. Specify title, author, type, and initial quantities.
    
    Args: 
      - title: Book title (non-empty)
      - author: Author name (non-empty)  
      - book_type: Type (fantasy, criminal, drama)
      - total_qty: Total copies in library
      - available_qty: Currently available copies
    
    Returns: Created book with UUID
    Raises: 403 if not admin
    """
    return BookService().create(data, actor_id=current_user.id)


@router.patch("/{book_id}", response_model=BookPublic)
def update_book(book_id: str, data: BookUpdate, current_user: UserInDB = Depends(require_role(Role.ADMIN))):
    """Update book information (title, author, quantities, etc).
    
    Admin only. Only supplied fields are updated.
    
    Returns: Updated book or 404 if not found
    Raises: 403 if not admin
    """
    try:
        return BookService().update(book_id, data, actor_id=current_user.id)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: str, current_user: UserInDB = Depends(require_role(Role.ADMIN))):
    """Remove a book from the catalog.
    
    Admin only. Soft-deletes the book (no cascade on borrows).
    
    Returns: 204 No Content on success
    Raises: 404 if not found, 403 if not admin
    """
    try:
        BookService().delete(book_id, actor_id=current_user.id)
    except ValueError as e:
        raise HTTPException(404, str(e))

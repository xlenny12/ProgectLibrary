from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_current_user, require_role
from app.models.borrow import BorrowCreate, BorrowPublic
from app.models.user import UserInDB, Role
from app.services.borrow_service import BorrowService

router = APIRouter(prefix="/api/borrows", tags=["borrows"])


@router.post("", response_model=BorrowPublic, status_code=status.HTTP_201_CREATED)
def borrow_book(data: BorrowCreate, current_user: UserInDB = Depends(get_current_user)):
    """Borrow a book.
    
    Any authenticated user can borrow. Decrements available quantity.
    Specify book ID, desired quantity, and borrow period (1-365 days).
    
    Returns: Borrow record with ID, due date, and status
    Raises: 400 if insufficient copies or book not found
    Raises: 409 (Conflict) if borrow fails due to race condition
    """
    try:
        return BorrowService().borrow(current_user.id, data)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/me", response_model=list[BorrowPublic])
def my_borrows(current_user: UserInDB = Depends(get_current_user)):
    """Get all borrows for the current user.
    
    Returns both active (unreturned) and completed (returned) borrow records.
    
    Returns: List of borrow records with dates, due dates, and return status
    """
    return BorrowService().my_borrows(current_user.id)


@router.post("/{borrow_id}/return", response_model=BorrowPublic)
def return_book(borrow_id: str, current_user: UserInDB = Depends(get_current_user)):
    """Return a borrowed book.
    
    Users can only return their own borrows. Restores available quantity.
    Marks borrow as returned and records return via audit log.
    
    Args: borrow_id - UUID of the borrow record
    Returns: Updated borrow record with returned=true
    Raises: 400 if not found or already returned, 403 if not the borrower
    """
    try:
        return BorrowService().return_book(borrow_id, current_user.id)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/overdue", response_model=list[BorrowPublic])
def overdue(_=Depends(require_role(Role.ADMIN, Role.ADVANCED))):
    """List all overdue borrows across the system.
    
    Admin and Advanced users only. Shows all unreturned books past their due date.
    
    Returns: List of overdue borrow records
    Raises: 403 if insufficient permissions
    """
    return BorrowService().overdue_borrows()

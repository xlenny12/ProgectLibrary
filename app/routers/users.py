from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user, require_role
from app.models.user import UserInDB, UserPublic, UserSelf, UserUpdate, Role
from app.services.user_service import UserService
from app.services.borrow_service import BorrowService

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserSelf)
def get_me(current_user: UserInDB = Depends(get_current_user)):
    """Get current user's full profile.
    
    Requires authentication. Users can only see their own profile via this endpoint.
    
    Returns: User with personal data (email, phone, address, DOB)
    """
    return UserService().get_self(current_user.id)


@router.patch("/me", response_model=UserSelf)
def update_me(data: UserUpdate, current_user: UserInDB = Depends(get_current_user)):
    """Update current user's profile.
    
    Users can update their own name, email, phone, address, and DOB.
    Only supplied fields are modified.
    
    Returns: Updated user profile or 400 if validation fails
    """
    try:
        return UserService().update(current_user.id, data, actor_id=current_user.id)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.delete("/me", status_code=204)
def delete_me(current_user: UserInDB = Depends(get_current_user)):
    """Delete current user account and all associated data (GDPR).
    
    Removes:
    - User profile
    - All borrow records
    - All audit entries for this user
    
    This action is permanent. Returns 204 No Content.
    """
    BorrowService().delete_all_for_user(current_user.id, actor_id=current_user.id)
    UserService().delete(current_user.id, actor_id=current_user.id)


@router.get("", response_model=list[UserPublic])
def list_users(_=Depends(require_role(Role.ADMIN, Role.ADVANCED))):
    """List all users (limited public info).
    
    Admin and Advanced users only. Returns name and role only (no personal data).
    
    Returns: List of all users (ID, full name, role)
    Raises: 403 if insufficient permissions
    """
    return UserService().list_public()


@router.get("/{user_id}", response_model=UserPublic)
def get_user(user_id: str, _=Depends(require_role(Role.ADMIN, Role.ADVANCED))):
    """Get a user's public profile.
    
    Admin and Advanced users only. Returns name and role only.
    
    Args: user_id - UUID of the user
    Returns: User (ID, name, role) or 404 if not found
    Raises: 403 if insufficient permissions
    """
    try:
        return UserService().get_public(user_id)
    except ValueError as e:
        raise HTTPException(404, str(e))

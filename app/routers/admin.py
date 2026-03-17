from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import require_role
from app.models.user import UserInDB, Role
from app.services.user_service import UserService
from app.services.borrow_service import BorrowService
from app.services.notification_service import NotificationService
from app.repositories.user_repo import UserRepository
from app.core.audit import verify_integrity, replay_events

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.delete("/users/{user_id}", status_code=204)
def admin_delete_user(
    user_id: str,
    current_user: UserInDB = Depends(require_role(Role.ADMIN)),
):
    BorrowService().delete_all_for_user(user_id, actor_id=current_user.id)
    try:
        UserService().admin_delete(user_id, actor_id=current_user.id)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.post("/notify/overdue", summary="Send overdue reminders (Advanced user or Admin)")
def notify_overdue(
    use_sms: bool = True,
    current_user: UserInDB = Depends(require_role(Role.ADMIN, Role.ADVANCED)),
):
    overdue = BorrowService().overdue_borrows()
    repo = UserRepository()
    svc = NotificationService()
    results = []
    for borrow in overdue:
        user = repo.find_by_id(borrow.user_id)
        if not user:
            continue
        ok = svc.send_overdue_sms(user, borrow) if use_sms else svc.send_overdue_email(user, borrow)
        results.append({"borrow_id": borrow.id, "user_id": borrow.user_id, "sent": ok})
    return {"notified": len(results), "results": results}


@router.get("/audit/verify", summary="Check audit log integrity")
def audit_verify(_=Depends(require_role(Role.ADMIN))):
    ok, tampered = verify_integrity()
    return {"integrity_ok": ok, "tampered_count": len(tampered)}


@router.get("/audit/replay", summary="Replay audit log for DB recovery")
def audit_replay(_=Depends(require_role(Role.ADMIN))):
    return replay_events()

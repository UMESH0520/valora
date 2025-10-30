from fastapi import Depends, HTTPException, status
from typing import List
from app.models.user import User, UserRole
from app.auth.jwt_handler import get_current_active_user


def require_role(allowed_roles: List[UserRole]):
    """
    Dependency factory to require specific roles for endpoints
    Usage: @router.get("/admin", dependencies=[Depends(require_role([UserRole.ADMIN]))])
    """
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in allowed_roles]}"
            )
        return current_user
    return role_checker

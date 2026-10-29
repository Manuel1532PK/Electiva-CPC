from fastapi import Depends, HTTPException, status
from app.auth.dependencies import get_current_user
from app.models.user import UserOut

ROLE_HIERARCHY = {
    "super_admin": 3,
    "admin": 2,
    "medico": 1,
    "paciente": 0,
}


def require_roles(*roles: str):
    allowed = set(roles)

    async def checker(current_user: UserOut = Depends(get_current_user)):
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role(s): {', '.join(sorted(allowed))}",
            )
        return current_user

    return checker


def require_min_role(min_role: str):
    min_level = ROLE_HIERARCHY.get(min_role, 0)

    async def checker(current_user: UserOut = Depends(get_current_user)):
        level = ROLE_HIERARCHY.get(current_user.role, -1)
        if level < min_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role at least: {min_role}",
            )
        return current_user

    return checker

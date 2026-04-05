from enum import Enum


class UserRole(str, Enum):
    VIEWER = "viewer"
    ANALYST = "analyst"
    ADMIN = "admin"


ROLE_HIERARCHY: dict[UserRole, int] = {
    UserRole.VIEWER: 1,
    UserRole.ANALYST: 2,
    UserRole.ADMIN: 3,
}


def has_minimum_role(current_role: UserRole, required_role: UserRole) -> bool:
    return ROLE_HIERARCHY[current_role] >= ROLE_HIERARCHY[required_role]

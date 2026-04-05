from sqlalchemy.orm import Session

from app.core.exceptions import APIError
from app.core.rbac import UserRole
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    token_expiry_to_datetime,
    verify_password,
)
from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.revoked_token_repository import RevokedTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import BootstrapAdminRequest, LoginRequest, TokenResponse


class AuthService:
    def __init__(self, db: Session) -> None:
        self.users = UserRepository(db)
        self.audit = AuditRepository(db)
        self.revoked_tokens = RevokedTokenRepository(db)

    def bootstrap_admin(self, payload: BootstrapAdminRequest) -> User:
        if self.users.exists_any():
            raise APIError(
                status_code=409,
                message="Bootstrap admin is already configured.",
                code="conflict",
            )

        if self.users.get_by_email(payload.email):
            raise APIError(status_code=409, message="Email is already in use.", code="conflict")

        admin = User(
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
            role=UserRole.ADMIN,
            is_active=True,
        )
        created = self.users.create(admin)
        self.audit.create_log(
            actor_id=created.id,
            action="bootstrap_admin",
            entity_type="user",
            entity_id=str(created.id),
        )
        return created

    def login(self, payload: LoginRequest) -> TokenResponse:
        user = self.users.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.hashed_password):
            raise APIError(status_code=401, message="Invalid email or password.", code="auth_error")

        if not user.is_active:
            raise APIError(status_code=403, message="User account is inactive.", code="forbidden")

        access_token = create_access_token(subject=str(user.id), role=user.role.value)
        refresh_token = create_refresh_token(subject=str(user.id), role=user.role.value)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    def refresh(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if payload.token_type != "refresh":
            raise APIError(status_code=401, message="Invalid refresh token.", code="auth_error")

        if self.revoked_tokens.is_revoked(payload.jti):
            raise APIError(status_code=401, message="Refresh token is revoked.", code="auth_error")

        user = self.users.get_by_id(int(payload.sub))
        if not user or not user.is_active:
            raise APIError(
                status_code=401,
                message="Refresh token is no longer valid.",
                code="auth_error",
            )

        self.revoked_tokens.revoke_token(
            jti=payload.jti,
            token_type=payload.token_type,
            subject_id=int(payload.sub),
            expires_at=token_expiry_to_datetime(payload.exp),
        )

        access_token = create_access_token(subject=str(user.id), role=user.role.value)
        next_refresh_token = create_refresh_token(subject=str(user.id), role=user.role.value)
        return TokenResponse(access_token=access_token, refresh_token=next_refresh_token)

    def logout(
        self,
        *,
        access_token: str,
        refresh_token: str | None,
        actor_id: int | None,
    ) -> None:
        access_payload = decode_token(access_token)
        if access_payload.token_type != "access":
            raise APIError(status_code=401, message="Invalid access token.", code="auth_error")

        self.revoked_tokens.revoke_token(
            jti=access_payload.jti,
            token_type=access_payload.token_type,
            subject_id=int(access_payload.sub),
            expires_at=token_expiry_to_datetime(access_payload.exp),
        )

        if refresh_token:
            refresh_payload = decode_token(refresh_token)
            if refresh_payload.token_type != "refresh":
                raise APIError(
                    status_code=401,
                    message="Invalid refresh token.",
                    code="auth_error",
                )

            if refresh_payload.sub != access_payload.sub:
                raise APIError(
                    status_code=400,
                    message="Refresh token does not belong to the current user.",
                    code="invalid_input",
                )

            self.revoked_tokens.revoke_token(
                jti=refresh_payload.jti,
                token_type=refresh_payload.token_type,
                subject_id=int(refresh_payload.sub),
                expires_at=token_expiry_to_datetime(refresh_payload.exp),
            )

        self.audit.create_log(
            actor_id=actor_id,
            action="logout",
            entity_type="user",
            entity_id=access_payload.sub,
        )

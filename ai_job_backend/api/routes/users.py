"""
Users API – assignment contract: POST /api/users, GET /api/users/{userId}.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from api import models
from api.dependencies import bcrypt_context, db_dependency, user_dependency
from api.limiter import limiter
from api.schemas import UserCreate, UserResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["users"])


@router.post("/users", status_code=201)
@limiter.exempt
def create_user(payload: UserCreate, db: db_dependency):
    """
    POST /api/users – Create a new user profile.
    Same semantics as POST /auth/register; provided for assignment contract.
    """
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        logger.warning("Create user failed: email already registered", extra={"email": payload.email})
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = bcrypt_context.hash(payload.password)
    new_user = models.User(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hashed_password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info("User created", extra={"user_id": new_user.id, "email": new_user.email})
    return {"id": new_user.id, "email": new_user.email, "full_name": new_user.full_name}


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: db_dependency, user: user_dependency):
    """
    GET /api/users/{userId} – Fetch a user profile (no password).
    Requires JWT. Returns 404 if user not found.
    """
    target = db.query(models.User).filter(models.User.id == user_id).first()
    if not target:
        logger.info("User not found", extra={"user_id": user_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.model_validate(target)

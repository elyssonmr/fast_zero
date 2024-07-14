from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero import security
from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import UserList, UserPublic, UserSchema

router = APIRouter(prefix='/users', tags=['Users'])

T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(security.get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def save_user(session: T_Session, user: UserSchema):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        field = 'Username' if db_user.username == user.username else 'Email'
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f'{field} already exists',
        )

    password = security.get_password_hash(user.password)
    db_user = User(username=user.username, password=password, email=user.email)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.put('/{user_id}', response_model=UserPublic)
def update_user(
    session: T_Session,
    user_id: int,
    user: UserSchema,
    current_user: T_CurrentUser,
):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permission'
        )

    current_user.username = user.username
    current_user.email = user.email
    current_user.password = security.get_password_hash(user.password)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return current_user


@router.get('/', response_model=UserList)
def get_users(session: T_Session, skip: int = 0, limit: int = 100):
    users = session.scalars(select(User).offset(skip).limit(limit)).all()
    return {'users': users}


@router.get('/{user_id}', response_model=UserPublic)
def get_user(session: T_Session, user_id: int):
    db_user = session.scalar(select(User).where(User.id == user_id))
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    return db_user


@router.delete('/{user_id}', response_model=UserPublic)
def delete_user(
    session: T_Session,
    user_id: int,
    current_user: T_CurrentUser,
):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permission'
        )

    session.delete(current_user)
    session.commit()
    return current_user

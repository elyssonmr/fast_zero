from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero import security
from fast_zero.database import get_async_session
from fast_zero.models import User
from fast_zero.schemas import Token

router = APIRouter(prefix='/auth', tags=['Auth'])

T_FormData = Annotated[OAuth2PasswordRequestForm, Depends()]
T_AsyncSession = Annotated[Session, Depends(get_async_session)]


@router.post('/token', response_model=Token)
async def login_for_token(session: T_AsyncSession, form_data: T_FormData):
    user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )

    if not user or not security.verify_password(
        form_data.password, user.password
    ):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Incorrect email or password',
        )

    data = {'sub': user.email}
    access_token = security.create_access_token(data)

    return Token(access_token=access_token, token_type='Bearer')


@router.post('/refresh_token', response_model=Token)
def refresh_access_token(
    user: User = Depends(security.get_current_user_async),
):
    new_access_token = security.create_access_token(data={'sub': user.email})

    return Token(access_token=new_access_token, token_type='bearer')

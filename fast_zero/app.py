from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero import security
from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Message, Token, UserList, UserPublic, UserSchema

app = FastAPI()


database = []

html_content = """
<html>
    <head>
        <title>Olá Mundo!!</title>
    </head>
    <body>
        <h1>Olá Mundo!!</h1>
    </body>
</html>
"""


@app.get('/hello_text', response_class=HTMLResponse)
def hello_text():
    return HTMLResponse(html_content)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def hello():
    return {'message': 'Olá Mundo!'}


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def save_user(user: UserSchema, session: Session = Depends(get_session)):
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


@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session = Depends(get_session),
    current_user=Depends(security.get_current_user),
):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Not enough permission'
        )

    current_user.username = user.username
    current_user.email = user.email
    current_user.password = security.get_password_hash(user.password)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return current_user


@app.get('/users/', response_model=UserList)
def get_users(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    users = session.scalars(select(User).offset(skip).limit(limit)).all()
    return {'users': users}


@app.get('/users/{user_id}', response_model=UserPublic)
def get_user(user_id: int, session: Session = Depends(get_session)):
    db_user = session.scalar(select(User).where(User.id == user_id))
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    return db_user


@app.delete('/users/{user_id}', response_model=UserPublic)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(security.get_current_user),
):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Not enough permission'
        )

    session.delete(current_user)
    session.commit()
    return current_user


@app.post('/token', response_model=Token)
def login_for_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.email == form_data.username))

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

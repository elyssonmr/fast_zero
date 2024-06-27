from http import HTTPStatus

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from fast_zero.schemas import Message, UserDB, UserList, UserPublic, UserSchema

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
def save_user(user: UserSchema):
    user_with_id = UserDB(id=len(database) + 1, **user.model_dump())
    database.append(user_with_id)
    return user_with_id


@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(user_id: int, user: UserSchema):
    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    user_db = UserDB(id=user_id, **user.model_dump())
    database[user_id - 1] = user_db
    return user_db


@app.get('/users/', response_model=UserList)
def get_users():
    return {'users': database}


@app.get('/users/{user_id}', response_model=UserPublic)
def get_user(user_id: int):
    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    return database[user_id - 1]


@app.delete('/users/{user_id}', response_model=UserPublic)
def delete_user(user_id: int):
    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    user = database.pop(user_id - 1)
    return user

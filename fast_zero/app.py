from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from fast_zero.routes import auth, users
from fast_zero.schemas import Message

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


# Routers
app.include_router(users.router)
app.include_router(auth.router)

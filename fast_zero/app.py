from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get('/')
def hello():
    return {'message': 'Olá Mundo!'}


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

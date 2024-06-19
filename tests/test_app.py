from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from fast_zero.app import app, html_content


@pytest.fixture()
def client():
    return TestClient(app)


def test_should_return_helloworld_json(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá Mundo!'}


def test_should_return_helloworld_html(client):
    response = client.get('/hello_text')

    assert response.status_code == HTTPStatus.OK
    assert 'Olá Mundo!!' in response.text
    assert response.text == html_content

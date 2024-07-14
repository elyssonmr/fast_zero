from http import HTTPStatus


def test_should_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    assert response.status_code == HTTPStatus.OK
    token = response.json()
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token


def test_create_access_token_should_return_bad_request(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': 'wrong_passwd'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    token = response.json()
    assert token['detail'] == 'Incorrect email or password'

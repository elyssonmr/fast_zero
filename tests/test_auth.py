from http import HTTPStatus

from freezegun import freeze_time


def test_should_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': user.clean_password,
        },
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


def test_create_access_token_should_return_bad_request_when_wrong_email(
    client, user
):
    response = client.post(
        '/auth/token',
        data={'username': 'wrong@email.com', 'password': user.clean_password},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    token = response.json()
    assert token['detail'] == 'Incorrect email or password'


def test_should_return_expired_token_after_time(client, user):
    with freeze_time('2000-01-01 00:00:00'):
        response = client.post(
            '/auth/token',
            data={
                'username': user.email,
                'password': user.clean_password,
            },
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2000-01-01 00:31:00'):
        response = client.put(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'Sbroubous',
                'email': 'sbroubous@transamerica.com',
                'password': '123456',
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


def test_should_refresh_valid_token(client, user):
    with freeze_time('2000-01-01 00:00:00'):
        response = client.post(
            '/auth/token',
            data={
                'username': user.email,
                'password': user.clean_password,
            },
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2000-01-01 00:25:00'):
        response = client.post(
            '/auth/refresh_token', headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == HTTPStatus.OK
        refreshed_token = response.json()
        assert 'access_token' in refreshed_token
        assert refreshed_token['token_type'] == 'bearer'


def test_should_not_refresh_expired_token(client, user):
    with freeze_time('2000-01-01 00:00:00'):
        response = client.post(
            '/auth/token',
            data={
                'username': user.email,
                'password': user.clean_password,
            },
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2000-01-01 00:31:00'):
        response = client.post(
            '/auth/refresh_token', headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json()['detail'] == 'Could not validate credentials'

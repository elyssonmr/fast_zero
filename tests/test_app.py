from http import HTTPStatus

from fast_zero.app import html_content
from fast_zero.schemas import UserPublic, UserSchema


def test_should_return_helloworld_json(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá Mundo!'}


def test_should_return_helloworld_html(client):
    response = client.get('/hello_text')

    assert response.status_code == HTTPStatus.OK
    assert 'Olá Mundo!!' in response.text
    assert response.text == html_content


def test_should_save_new_user_with_id(client):
    response = client.post(
        '/users/',
        json={
            'username': 'Sbrubbles',
            'email': 'sbrubbles@transamerica.com',
            'password': 'sbroubous',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'Sbrubbles',
        'email': 'sbrubbles@transamerica.com',
    }


def test_should_raise_bad_request_same_username(client, user):
    user_schema = UserSchema.model_validate(user).model_dump()
    response = client.post('/users/', json=user_schema)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Username already exists'}


def test_should_raise_bad_request_same_email(client, user):
    user_schema = UserSchema.model_validate(user).model_dump()
    user_schema['username'] = 'new_username'
    response = client.post('/users/', json=user_schema)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Email already exists'}


def test_should_return_users_list(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_should_return_updated_user(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    user_schema['username'] = 'Updated Name'
    user_request = {
        'username': user_schema['username'],
        'email': user.email,
        'password': user.password,
    }
    response_put = client.put(f'/users/{user.id}', json=user_request)

    assert response_put.status_code == HTTPStatus.OK
    assert response_put.json() == user_schema


def test_should_raise_not_found(client):
    user_id = 1000000000
    response = client.put(
        f'/users/{user_id}',
        json={
            'username': 'Sbroubous',
            'email': 'sbroubous@transamerica.com',
            'password': '123456',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_should_return_deleted_user_while_delete(client, user):
    expected_response = UserPublic.model_validate(user).model_dump()

    response = client.delete(f'/users/{user.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected_response


def test_should_return_not_found_while_delete_user(client):
    user_id = 100000000
    response = client.delete(f'/users/{user_id}')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_should_return_one_user(client, user):
    expected_user = UserPublic.model_validate(user).model_dump()

    response = client.get(f'/users/{user.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected_user


def test_should_return_not_found_while_get_user(client):
    user_id = 100000000
    response = client.get(f'/users/{user_id}')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}

from http import HTTPStatus

from fast_zero.schemas import UserPublic, UserSchema


def test_should_return_users_list(async_client, async_user):
    user_schema = UserPublic.model_validate(async_user).model_dump()
    response = async_client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_should_save_new_user_with_id(async_client):
    response = async_client.post(
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


def test_should_raise_bad_request_same_username(async_client, async_user):
    user_schema = UserSchema.model_validate(async_user).model_dump()
    response = async_client.post('/users/', json=user_schema)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Username already exists'}


def test_should_raise_bad_request_same_email(async_client, async_user):
    user_schema = UserSchema.model_validate(async_user).model_dump()
    user_schema['username'] = 'new_username'
    response = async_client.post('/users/', json=user_schema)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Email already exists'}


def test_should_return_updated_user(async_client, async_user, async_token):
    user_schema = UserPublic.model_validate(async_user).model_dump()
    user_schema['username'] = 'Updated Name'
    user_request = {
        'username': user_schema['username'],
        'email': async_user.email,
        'password': async_user.password,
    }
    response_put = async_client.put(
        f'/users/{async_user.id}',
        headers={'Authorization': f'Bearer {async_token}'},
        json=user_request,
    )

    assert response_put.status_code == HTTPStatus.OK
    assert response_put.json() == user_schema

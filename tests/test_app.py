from http import HTTPStatus

from fast_zero.app import html_content


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


def test_should_return_users_list(client):
    users = [
        {
            'username': 'Sbroubous',
            'email': 'sbroubous@transamerica.com',
            'password': '123456',
        },
        {
            'username': 'Sbroubous2',
            'email': 'sbroubous@transamerica.com',
            'password': '123456',
        },
    ]

    response_users = []
    for user in users:
        response = client.post('/users/', json=user)
        assert response.status_code == HTTPStatus.CREATED
        response_users.append(response.json())

    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    get_users = response.json()['users']

    for user in response_users:
        assert user in get_users


def test_should_return_updated_user(client):
    user = {
        'username': 'Sbroubous',
        'email': 'sbroubous@transamerica.com',
        'password': '123456',
    }
    response_post = client.post('/users/', json=user)

    assert response_post.status_code == HTTPStatus.CREATED

    created_id = response_post.json()['id']

    user['username'] = 'Sbroubous2'
    expected_response = {
        'id': created_id,
        'username': user['username'],
        'email': user['email'],
    }
    response_put = client.put(f'/users/{created_id}', json=user)

    assert response_put.status_code == HTTPStatus.OK
    assert response_put.json() == expected_response


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


def test_should_return_deleted_user_while_update(client):
    user = {
        'username': 'Sbroubous',
        'email': 'sbroubous@transamerica.com',
        'password': '123456',
    }
    response_post = client.post('/users/', json=user)

    assert response_post.status_code == HTTPStatus.CREATED

    created_id = response_post.json()['id']
    expected_response = {
        'id': created_id,
        'username': 'Sbroubous',
        'email': 'sbroubous@transamerica.com',
    }

    response_detele = client.delete(f'/users/{created_id}')

    assert response_detele.status_code == HTTPStatus.OK
    assert response_detele.json() == expected_response


def test_should_return_not_found_while_delete_user(client):
    user_id = 100000000
    response_detele = client.delete(f'/users/{user_id}')

    assert response_detele.status_code == HTTPStatus.NOT_FOUND
    assert response_detele.json() == {'detail': 'User not found'}


def test_should_return_one_user(client):
    user = {
        'username': 'Sbroubous',
        'email': 'sbroubous@transamerica.com',
        'password': '123456',
    }

    response_post = client.post('/users/', json=user)

    assert response_post.status_code == HTTPStatus.CREATED

    created_id = response_post.json()['id']
    expected_response = {
        'id': created_id,
        'username': 'Sbroubous',
        'email': 'sbroubous@transamerica.com',
    }

    response_get = client.get(f'/users/{created_id}')

    assert response_get.status_code == HTTPStatus.OK
    assert response_get.json() == expected_response


def test_should_return_not_found_while_get_user(client):
    user_id = 100000000
    response_detele = client.get(f'/users/{user_id}')

    assert response_detele.status_code == HTTPStatus.NOT_FOUND
    assert response_detele.json() == {'detail': 'User not found'}

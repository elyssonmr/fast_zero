from http import HTTPStatus

import factory
import factory.fuzzy
from freezegun import freeze_time

from fast_zero.models import Todo, TodoState


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


def test_should_save_todo(client, token):
    with freeze_time('2000-01-01 00:00:00'):
        response = client.post(
            '/todos/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Test Todo',
                'description': 'test todo for post test',
                'state': 'draft',
            },
        )

    assert response.status_code == HTTPStatus.CREATED
    resp_todo = response.json()
    expected_values = {
        'id': 1,
        'title': 'Test Todo',
        'description': 'test todo for post test',
        'state': 'draft',
    }
    for key, value in expected_values.items():
        assert resp_todo[key] == value

    assert 'created_at' in resp_todo.keys()
    assert 'updated_at' in resp_todo.keys()


async def test_should_return_all_created_todos(session, client, user, token):
    expected_todos_count = 5

    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos_count


async def test_should_filter_by_title(session, client, user, token):
    todos = TodoFactory.create_batch(5, user_id=user.id)
    first_todo = todos[0]
    first_todo.title = 'sbroubous'

    session.add_all(todos)
    await session.commit()

    response = client.get(
        f'/todos/?title={first_todo.title[:5]}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == 1
    assert response.json()['todos'][0]['title'] == first_todo.title


async def test_should_filter_by_description(session, client, user, token):
    todos = TodoFactory.create_batch(5, user_id=user.id)
    first_todo = todos[0]
    first_todo.description = 'transamerica sbroubous'

    session.add_all(todos)
    await session.commit()

    response = client.get(
        f'/todos/?description={first_todo.description[10:20]}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == 1
    assert response.json()['todos'][0]['description'] == first_todo.description


async def test_should_filter_by_state(session, client, user, token):
    todos = TodoFactory.create_batch(5, user_id=user.id, state=TodoState.doing)
    first_todo = todos[0]
    first_todo.state = TodoState.done

    session.add_all(todos)
    await session.commit()

    response = client.get(
        '/todos/?state=done',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == 1
    assert response.json()['todos'][0]['title'] == first_todo.title
    assert response.json()['todos'][0]['state'] == TodoState.done


async def test_should_apply_pagination_limit(session, client, user, token):
    expected_todos_count = 2

    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/?offset=2&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos_count


async def test_should_filter_by_title_description(
    session, client, user, token
):
    expected_todos_count = 5

    session.add_all(
        TodoFactory.create_batch(
            5, user_id=user.id, title='sbroubous', state=TodoState.doing
        )
    )
    session.add_all(
        TodoFactory.create_batch(
            3,
            user_id=user.id,
            description='transamerica',
            state=TodoState.done,
        )
    )
    await session.commit()

    response = client.get(
        '/todos/?title=sbroub&state=doing',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK

    todos = response.json()['todos']
    assert len(todos) == expected_todos_count
    for todo in todos:
        assert todo['title'] == 'sbroubous'
        assert todo['state'] == TodoState.doing


async def test_should_delete_todo(session, client, user, token):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    await session.commit()
    await session.refresh(todo)

    response = client.delete(
        f'/todos/{todo.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Task has been deleted successfully'}


def test_delete_should_return_notfound(client, token):
    response = client.delete(
        '/todos/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


async def test_should_patch_todo(session, client, user, token):
    updated_title = 'todo updated'
    todo = TodoFactory(user_id=user.id, state=TodoState.doing)
    session.add(todo)
    await session.commit()
    await session.refresh(todo)

    response = client.patch(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': updated_title, 'state': TodoState.done},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == updated_title
    assert response.json()['state'] == TodoState.done


def test_patch_should_return_notfound(client, token):
    response = client.patch(
        '/todos/1', headers={'Authorization': f'Bearer {token}'}, json={}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}

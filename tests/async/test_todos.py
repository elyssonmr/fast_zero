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


def test_should_save_todo(async_client, async_token):
    with freeze_time('2000-01-01 00:00:00'):
        response = async_client.post(
            '/todos/',
            headers={'Authorization': f'Bearer {async_token}'},
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


async def test_should_return_all_created_todos(
    async_session, async_client, async_user, async_token
):
    expected_todos_count = 5

    async_session.add_all(TodoFactory.create_batch(5, user_id=async_user.id))
    await async_session.commit()

    response = async_client.get(
        '/todos/', headers={'Authorization': f'Bearer {async_token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos_count


async def test_should_filter_by_title(
    async_session, async_client, async_user, async_token
):
    todos = TodoFactory.create_batch(5, user_id=async_user.id)
    first_todo = todos[0]
    first_todo.title = 'sbroubous'

    async_session.add_all(todos)
    await async_session.commit()

    response = async_client.get(
        f'/todos/?title={first_todo.title[:5]}',
        headers={'Authorization': f'Bearer {async_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == 1
    assert response.json()['todos'][0]['title'] == first_todo.title


async def test_should_filter_by_description(
    async_session, async_client, async_user, async_token
):
    todos = TodoFactory.create_batch(5, user_id=async_user.id)
    first_todo = todos[0]
    first_todo.description = 'transamerica sbroubous'

    async_session.add_all(todos)
    await async_session.commit()

    response = async_client.get(
        f'/todos/?description={first_todo.description[10:20]}',
        headers={'Authorization': f'Bearer {async_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == 1
    assert response.json()['todos'][0]['description'] == first_todo.description


async def test_should_filter_by_state(
    async_session, async_client, user, async_token
):
    todos = TodoFactory.create_batch(5, user_id=user.id, state=TodoState.doing)
    first_todo = todos[0]
    first_todo.state = TodoState.done

    async_session.add_all(todos)
    await async_session.commit()

    response = async_client.get(
        '/todos/?state=done',
        headers={'Authorization': f'Bearer {async_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == 1
    assert response.json()['todos'][0]['title'] == first_todo.title
    assert response.json()['todos'][0]['state'] == TodoState.done


async def test_should_apply_pagination_limit(
    async_session, async_client, async_user, async_token
):
    expected_todos_count = 2

    async_session.add_all(TodoFactory.create_batch(5, user_id=async_user.id))
    await async_session.commit()

    response = async_client.get(
        '/todos/?offset=2&limit=2',
        headers={'Authorization': f'Bearer {async_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos_count


async def test_should_filter_by_title_description(
    async_session, async_client, async_user, async_token
):
    expected_todos_count = 5

    async_session.add_all(
        TodoFactory.create_batch(
            5, user_id=async_user.id, title='sbroubous', state=TodoState.doing
        )
    )
    async_session.add_all(
        TodoFactory.create_batch(
            3,
            user_id=async_user.id,
            description='transamerica',
            state=TodoState.done,
        )
    )
    await async_session.commit()

    response = async_client.get(
        '/todos/?title=sbroub&state=doing',
        headers={'Authorization': f'Bearer {async_token}'},
    )

    assert response.status_code == HTTPStatus.OK

    todos = response.json()['todos']
    assert len(todos) == expected_todos_count
    for todo in todos:
        assert todo['title'] == 'sbroubous'
        assert todo['state'] == TodoState.doing


async def test_should_delete_todo(
    async_session, async_client, async_user, async_token
):
    todo = TodoFactory(user_id=async_user.id)
    async_session.add(todo)
    await async_session.commit()
    await async_session.refresh(todo)

    response = async_client.delete(
        f'/todos/{todo.id}', headers={'Authorization': f'Bearer {async_token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Task has been deleted successfully'}


def test_delete_should_return_notfound(async_client, async_token):
    response = async_client.delete(
        '/todos/1', headers={'Authorization': f'Bearer {async_token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


async def test_should_patch_todo(
    async_session, async_client, async_user, async_token
):
    updated_title = 'todo updated'
    todo = TodoFactory(user_id=async_user.id, state=TodoState.doing)
    async_session.add(todo)
    await async_session.commit()
    await async_session.refresh(todo)

    response = async_client.patch(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {async_token}'},
        json={'title': updated_title, 'state': TodoState.done},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == updated_title
    assert response.json()['state'] == TodoState.done


def test_patch_should_return_notfound(async_client, async_token):
    response = async_client.patch(
        '/todos/1', headers={'Authorization': f'Bearer {async_token}'}, json={}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}

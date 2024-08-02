import factory
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer

from fast_zero import security
from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import User, table_registry


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'test{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@email.com')
    password = factory.LazyAttribute(
        lambda obj: security.get_password_hash(f'{obj.username}-passwd')
    )


@pytest.fixture(scope='session')
async def engine():
    with PostgresContainer('postgres:16-alpine', driver='psycopg') as postgres:
        engine = create_async_engine(postgres.get_connection_url())
        yield engine


@pytest.fixture()
async def session(engine):
    async with engine.connect() as conn:
        await conn.run_sync(table_registry.metadata.create_all)
        await conn.commit()

        async with AsyncSession(engine, expire_on_commit=False) as session:
            yield session

        await conn.run_sync(table_registry.metadata.drop_all)
        await conn.commit()


@pytest.fixture()
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture()
async def user(session):
    passwd = 'passwd'
    user = UserFactory(password=security.get_password_hash(passwd))
    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = passwd

    return user


@pytest.fixture()
async def other_user(session):
    user = UserFactory()
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


@pytest.fixture()
def token(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': user.clean_password,
        },
    )

    return response.json()['access_token']


@pytest.fixture()
def invalid_token():
    data = {'sub': 'invalid_username@email.com'}
    return security.create_access_token(data)


@pytest.fixture()
def no_valid_field_token():
    data = {'iss': 'invalid_username@email.com'}
    return security.create_access_token(data)

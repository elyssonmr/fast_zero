import factory
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer

from fast_zero import security
from fast_zero.app import app
from fast_zero.database import get_async_session
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
async def async_engine():
    with PostgresContainer('postgres:16-alpine', driver='psycopg') as postgres:
        engine = create_async_engine(postgres.get_connection_url())
        yield engine


@pytest.fixture()
async def async_session(async_engine: AsyncEngine):
    async with async_engine.connect() as conn:
        await conn.run_sync(table_registry.metadata.create_all)
        await conn.commit()

        async with AsyncSession(
            async_engine, expire_on_commit=False
        ) as session:
            yield session

        await conn.run_sync(table_registry.metadata.drop_all)
        await conn.commit()


@pytest.fixture()
def async_client(async_session):
    def get_async_session_override():
        return async_session

    with TestClient(app) as client:
        app.dependency_overrides[get_async_session] = (
            get_async_session_override
        )
        yield client

    app.dependency_overrides.clear()


@pytest.fixture()
async def async_user(async_session):
    passwd = 'passwd'
    user = UserFactory(password=security.get_password_hash(passwd))
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)

    user.clean_password = passwd

    return user


@pytest.fixture()
def user(async_user):
    return async_user


@pytest.fixture()
def async_token(async_client, async_user):
    response = async_client.post(
        '/auth/token',
        data={
            'username': async_user.email,
            'password': async_user.clean_password,
        },
    )

    return response.json()['access_token']

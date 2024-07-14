import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from fast_zero import security
from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import User, table_registry


@pytest.fixture()
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)


@pytest.fixture()
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture()
def user(session):
    passwd = 'passwd'
    user = User(
        username='test',
        email='teste@email.com',
        password=security.get_password_hash(passwd),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = passwd

    return user


@pytest.fixture()
def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
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

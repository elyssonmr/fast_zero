from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session):
    new_user = User(username='Alice', password='secret', email='test@test.com')
    session.add(new_user)
    session.commit()

    user = session.scalar(select(User).where(User.username == 'Alice'))

    assert user.username == new_user.username

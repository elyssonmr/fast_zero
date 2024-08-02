from sqlalchemy import select

from fast_zero.models import User


async def test_create_user(async_session):
    new_user = User(username='Alice', password='secret', email='test@test.com')
    async_session.add(new_user)
    await async_session.commit()

    user = await async_session.scalar(
        select(User).where(User.username == 'Alice')
    )

    assert user.username == new_user.username

from jwt import decode

from fast_zero import security
from fast_zero.settings import Settings

settings = Settings()


def test_get_password_should_call_hash():
    pass


def test_verify_password_should_call_verify():
    pass


def test_create_access_token_should_generate_valid_jwt():
    data = {'sub': 'test@test.com'}

    token = security.create_access_token(data)

    result = decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )

    assert result['sub'] == data['sub']
    assert 'exp' in result.keys()

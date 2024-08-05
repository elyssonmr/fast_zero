from unittest.mock import patch

from jwt import decode

from fast_zero import security
from fast_zero.settings import Settings

settings = Settings()


def test_get_password_should_call_hash():
    with patch('fast_zero.security.pwd_context') as _pwd_context:
        password = 'passwd'
        _pwd_context.hash.return_value = 'hashed_passwd'
        result = security.get_password_hash(password)

        assert result == 'hashed_passwd'
        _pwd_context.hash.assert_called_once_with(password)


def test_verify_password_should_call_verify():
    with patch('fast_zero.security.pwd_context') as _pwd_context:
        password = 'passwd'
        hashed_passwd = 'hashed_passwd'
        _pwd_context.verify.return_value = True
        result = security.verify_password(password, hashed_passwd)

        assert result
        _pwd_context.verify.assert_called_once_with(password, hashed_passwd)


def test_create_access_token_should_generate_valid_jwt():
    data = {'sub': 'test@test.com'}

    token = security.create_access_token(data)

    result = decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )

    assert result['sub'] == data['sub']
    assert 'exp' in result.keys()

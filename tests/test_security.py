from jwt import decode

from fast_zero import security


def test_get_password_should_call_hash():
    pass


def test_verify_password_should_call_verify():
    pass


def test_create_access_token_should_generate_valid_jwt():
    data = {'sub': 'test@test.com'}

    token = security.create_access_token(data)

    result = decode(
        token, security.SECRET_KEY, algorithms=[security.ALGORITHM]
    )

    assert result['sub'] == data['sub']
    assert 'exp' in result.keys()

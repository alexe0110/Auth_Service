import jwt
from httpx import Cookies


def check_jwt_tokens(cookies: Cookies, user_account_id: str):
    access_token = cookies.get("access_token")
    refresh_token = cookies.get("refresh_token")

    assert access_token
    assert refresh_token

    decoded_access_token = jwt.decode(access_token, options={"verify_signature": False})
    decoded_refresh_token = jwt.decode(refresh_token, options={"verify_signature": False})

    assert decoded_access_token.get("account_id") == user_account_id
    assert decoded_refresh_token.get("account_id") == user_account_id

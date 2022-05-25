import os

OAUTH_BASE_URL = "https://pamiwjc.eu.auth0.com"
OAUTH_ACCESS_TOKEN_URL = OAUTH_BASE_URL + "/oauth/token"
OAUTH_AUTHORIZE_URL = OAUTH_BASE_URL + "/authorize"
OAUTH_CALLBACK_URL = "https://localhost:8080/callback"
OAUTH_CALLBACK_URL_COURIER = "https://localhost:8082/callback"
OAUTH_CLIENT_ID = "9cTghr1CGmgFXOwlA4woF0xv26F4wnEI"
OAUTH_CLIENT_SECRET = "1TWT1T2HjEcRgB8t0_1tiyglQBUU6YEwFq2-LjuS9a2s-GxM3sBjYDcFJCKAX20f"
OAUTH_SCOPE = "openid profile"
SECRET_KEY = os.environ.get("SECRET_KEY")
NICKNAME = "nickname"
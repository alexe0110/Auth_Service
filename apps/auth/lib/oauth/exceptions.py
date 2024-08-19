class OAuthBaseError(BaseException):
    pass


class OAuthGetTokenError(OAuthBaseError):
    pass


class OAuthLoginError(OAuthBaseError):
    pass

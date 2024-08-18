class YandexOAuthBaseError(BaseException):
    pass


class YandexGettingOAuthTokenError(YandexOAuthBaseError):
    pass


class YandexOAuthLoginError(YandexOAuthBaseError):
    pass

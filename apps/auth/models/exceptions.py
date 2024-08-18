class UserAlreadyExistError(Exception):
    msg = "User already registered"


class UserNotRegisteredError(Exception):
    msg = "User not registered"


class RoleAlreadyExistError(Exception):
    msg = "Role already exist"


class RoleNotExistError(Exception):
    msg = "Role not exist"


class UserRoleNotExistError(Exception):
    msg = "User does not have the specified role"


class UserRoleAlreadyExistError(Exception):
    msg = "User already have the specified role"


class GenerateTokensError(Exception):
    msg = "Exception occured while generating tokens"


class InvalidCredentialsError(Exception):
    msg = "Invalid credentials"


class UserNotExistsError(Exception):
    msg = "User not exists"


class UnknownExternalProviderError(Exception):
    msg = "Unknown external auth provider"

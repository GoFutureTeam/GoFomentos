"""
Domain Exceptions - Exceções específicas da camada de domínio
"""


class DomainException(Exception):
    """Exceção base para todas as exceções de domínio"""
    pass


# User Exceptions
class UserException(DomainException):
    """Exceção base para erros relacionados a usuários"""
    pass


class UserNotFoundError(UserException):
    """Usuário não encontrado"""
    def __init__(self, user_id: str = None, email: str = None):
        if user_id:
            message = f"User with id '{user_id}' not found"
        elif email:
            message = f"User with email '{email}' not found"
        else:
            message = "User not found"
        super().__init__(message)


class UserAlreadyExistsError(UserException):
    """Usuário já existe"""
    def __init__(self, email: str):
        super().__init__(f"User with email '{email}' already exists")


class InvalidCredentialsError(UserException):
    """Credenciais inválidas"""
    def __init__(self):
        super().__init__("Invalid email or password")


class UserInactiveError(UserException):
    """Usuário inativo"""
    def __init__(self):
        super().__init__("User account is inactive")


# Edital Exceptions
class EditalException(DomainException):
    """Exceção base para erros relacionados a editais"""
    pass


class EditalNotFoundError(EditalException):
    """Edital não encontrado"""
    def __init__(self, edital_uuid: str):
        super().__init__(f"Edital with uuid '{edital_uuid}' not found")


class EditalAlreadyExistsError(EditalException):
    """Edital já existe"""
    def __init__(self, link: str):
        super().__init__(f"Edital with link '{link}' already exists")


class EditalClosedError(EditalException):
    """Edital está fechado"""
    def __init__(self, edital_uuid: str):
        super().__init__(f"Edital '{edital_uuid}' is closed for submissions")


# Project Exceptions
class ProjectException(DomainException):
    """Exceção base para erros relacionados a projetos"""
    pass


class ProjectNotFoundError(ProjectException):
    """Projeto não encontrado"""
    def __init__(self, project_id: str):
        super().__init__(f"Project with id '{project_id}' not found")


class ProjectAccessDeniedError(ProjectException):
    """Acesso negado ao projeto"""
    def __init__(self, project_id: str, user_id: str):
        super().__init__(f"User '{user_id}' does not have access to project '{project_id}'")


class InvalidCNAEError(ProjectException):
    """CNAE inválido"""
    def __init__(self, cnae: str):
        super().__init__(f"Invalid CNAE: '{cnae}'")


# Authentication & Authorization Exceptions
class AuthenticationException(DomainException):
    """Exceção base para erros de autenticação"""
    pass


class InvalidTokenError(AuthenticationException):
    """Token inválido ou expirado"""
    def __init__(self):
        super().__init__("Invalid or expired token")


class AuthorizationException(DomainException):
    """Exceção base para erros de autorização"""
    pass


class InsufficientPermissionsError(AuthorizationException):
    """Permissões insuficientes"""
    def __init__(self, action: str):
        super().__init__(f"Insufficient permissions to perform action: '{action}'")


# Validation Exceptions
class ValidationException(DomainException):
    """Exceção base para erros de validação"""
    pass


class InvalidEmailError(ValidationException):
    """Email inválido"""
    def __init__(self, email: str):
        super().__init__(f"Invalid email format: '{email}'")


class WeakPasswordError(ValidationException):
    """Senha fraca"""
    def __init__(self):
        super().__init__("Password does not meet security requirements")


class InvalidDateRangeError(ValidationException):
    """Intervalo de datas inválido"""
    def __init__(self, field: str):
        super().__init__(f"Invalid date range for field: '{field}'")

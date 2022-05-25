class UnauthorizedUserError(Exception):
    pass


class BadRequestError(Exception):
    pass


class NotFoundError(Exception):
    pass


class ForbiddenError(Exception):
    pass
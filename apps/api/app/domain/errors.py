class DomainError(ValueError):
    pass


class GroundingError(DomainError):
    pass


class InsufficientContextError(GroundingError):
    pass

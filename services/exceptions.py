"""User-safe service exceptions."""


class SemsError(Exception):
    """Base exception whose message is safe to display to an application user."""


class ValidationError(SemsError):
    """Input or cross-table rule failed."""


class AuthorizationError(SemsError):
    """Authenticated actor is not permitted to perform an operation."""


class AuthenticationError(SemsError):
    """Demo authentication failed without exposing credential details."""


class NotFoundError(SemsError):
    """Requested domain record does not exist."""


class StateTransitionError(SemsError):
    """Requested workflow transition is not valid from the current state."""


class InsufficientStockError(SemsError):
    """A stock-changing operation would make a quantity negative."""


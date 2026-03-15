class TransactionError(Exception):
    """Base error for transaction domain."""


class InvalidTransactionError(TransactionError):
    pass


class TransactionAlreadySettledError(TransactionError):
    pass


class TransactionNotFoundError(TransactionError):
    pass


class TransactionImmutableError(TransactionError):
    """Raised when attempting to modify a terminal-status transaction (SETTLED, REVERSED)."""


class TransactionConcurrentUpdateError(TransactionError):
    """Raised when optimistic locking detects a concurrent modification. Client should retry."""


class DuplicateTransactionError(TransactionError):
    """Raised when an idempotency key has already been used for a different transaction."""

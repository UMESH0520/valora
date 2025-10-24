from fastapi import HTTPException, status


class ValoraException(Exception):
    """Base exception for Valora application"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ProductNotFoundException(ValoraException):
    """Raised when product is not found"""
    def __init__(self, product_id: str):
        super().__init__(
            message=f"Product not found: {product_id}",
            status_code=status.HTTP_404_NOT_FOUND
        )


class PriceDataNotFoundException(ValoraException):
    """Raised when no price data is available"""
    def __init__(self, product_id: str):
        super().__init__(
            message=f"No price data available for product: {product_id}",
            status_code=status.HTTP_404_NOT_FOUND
        )


class AdapterException(ValoraException):
    """Raised when all adapters fail"""
    def __init__(self, product_id: str):
        super().__init__(
            message=f"All price adapters failed for product: {product_id}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


class BlockchainException(ValoraException):
    """Raised when blockchain submission fails"""
    def __init__(self, message: str):
        super().__init__(
            message=f"Blockchain error: {message}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class DatabaseException(ValoraException):
    """Raised when database operation fails"""
    def __init__(self, message: str):
        super().__init__(
            message=f"Database error: {message}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ValidationException(ValoraException):
    """Raised when validation fails"""
    def __init__(self, message: str):
        super().__init__(
            message=f"Validation error: {message}",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class AuthenticationException(ValoraException):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationException(ValoraException):
    """Raised when authorization fails"""
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )


class RateLimitException(ValoraException):
    """Raised when rate limit is exceeded"""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )


def convert_to_http_exception(exc: ValoraException) -> HTTPException:
    """Convert custom exception to FastAPI HTTPException"""
    return HTTPException(
        status_code=exc.status_code,
        detail=exc.message
    )

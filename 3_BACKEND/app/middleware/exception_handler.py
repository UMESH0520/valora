from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.exceptions import ValoraException

logger = logging.getLogger('valora.exception_handler')


async def valora_exception_handler(request: Request, exc: ValoraException):
    """Handle custom Valora exceptions"""
    logger.error(f"ValoraException: {exc.message}", extra={
        'path': request.url.path,
        'method': request.method,
        'status_code': exc.status_code
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'error': exc.__class__.__name__,
            'message': exc.message,
            'path': request.url.path
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    logger.warning(f"Validation error: {exc.errors()}", extra={
        'path': request.url.path,
        'method': request.method
    })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            'error': 'ValidationError',
            'message': 'Request validation failed',
            'details': exc.errors(),
            'path': request.url.path
        }
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle SQLAlchemy database errors"""
    logger.exception("Database error occurred", extra={
        'path': request.url.path,
        'method': request.method
    })
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            'error': 'DatabaseError',
            'message': 'A database error occurred',
            'path': request.url.path
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handle any uncaught exceptions"""
    logger.exception("Unexpected error occurred", extra={
        'path': request.url.path,
        'method': request.method,
        'exception_type': type(exc).__name__
    })
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            'error': 'InternalServerError',
            'message': 'An unexpected error occurred',
            'path': request.url.path
        }
    )

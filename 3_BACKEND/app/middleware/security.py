import os
import re
import time
import logging
from typing import List, Dict, Set, Optional
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.datastructures import Headers

logger = logging.getLogger('valora.security')


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add comprehensive security headers to all responses
    """
    
    def __init__(self, app, environment: str = "development"):
        super().__init__(app)
        self.environment = environment
    
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        
        # Security headers
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'camera=(), microphone=(), geolocation=(), payment=()',
        }
        
        # Content Security Policy
        if self.environment == "production":
            security_headers['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "connect-src 'self'; "
                "font-src 'self'; "
                "frame-ancestors 'none';"
            )
            # HSTS for production
            security_headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Add all security headers
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Limit request body size to prevent DoS attacks
    """
    
    def __init__(self, app, max_size_bytes: int = 1024 * 1024):  # 1MB default
        super().__init__(app)
        self.max_size_bytes = max_size_bytes
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Check Content-Length header
        content_length = request.headers.get('Content-Length')
        if content_length:
            try:
                size = int(content_length)
                if size > self.max_size_bytes:
                    logger.warning(
                        f"Request size {size} exceeds limit {self.max_size_bytes}",
                        extra={'client_ip': request.client.host, 'path': request.url.path}
                    )
                    return JSONResponse(
                        status_code=413,
                        content={
                            'error': 'PayloadTooLarge',
                            'message': f'Request size {size} bytes exceeds maximum {self.max_size_bytes} bytes',
                            'max_size_bytes': self.max_size_bytes
                        }
                    )
            except ValueError:
                pass  # Invalid Content-Length header, let it through
        
        return await call_next(request)


class IPSecurityMiddleware(BaseHTTPMiddleware):
    """
    IP-based security with blocklists and suspicious pattern detection
    """
    
    def __init__(
        self,
        app,
        blocked_ips: Optional[Set[str]] = None,
        allowed_ips: Optional[Set[str]] = None,
        enable_suspicious_detection: bool = True
    ):
        super().__init__(app)
        self.blocked_ips = blocked_ips or set()
        self.allowed_ips = allowed_ips  # If set, only these IPs are allowed
        self.enable_suspicious_detection = enable_suspicious_detection
        
        # Suspicious patterns in URLs and headers
        self.suspicious_patterns = [
            # SQL Injection patterns
            re.compile(r"(?i)(union\s+select|script\s*>|drop\s+table)", re.IGNORECASE),
            # XSS patterns
            re.compile(r"(?i)(<script|javascript:|data:text/html)", re.IGNORECASE),
            # Path traversal
            re.compile(r"(\.\./|\.\.\\|%2e%2e%2f|%2e%2e\\)", re.IGNORECASE),
            # Command injection
            re.compile(r"(?i)(;|\||`|&|\$\(|\$\{)", re.IGNORECASE),
        ]
        
        # Track suspicious activity
        self.suspicious_activity: Dict[str, List[float]] = {}
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP considering proxy headers"""
        # Check X-Forwarded-For (from load balancer/proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP (original client)
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP (nginx)
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fallback to direct connection
        return request.client.host if request.client else "unknown"
    
    def _is_suspicious_request(self, request: Request) -> bool:
        """Check if request contains suspicious patterns"""
        if not self.enable_suspicious_detection:
            return False
        
        # Check URL path and query parameters
        full_url = str(request.url)
        
        for pattern in self.suspicious_patterns:
            if pattern.search(full_url):
                logger.warning(
                    f"Suspicious pattern detected in URL: {pattern.pattern}",
                    extra={'url': full_url, 'client_ip': self._get_client_ip(request)}
                )
                return True
        
        # Check common headers
        suspicious_headers = ['User-Agent', 'Referer', 'X-Forwarded-Host']
        for header_name in suspicious_headers:
            header_value = request.headers.get(header_name, "")
            for pattern in self.suspicious_patterns:
                if pattern.search(header_value):
                    logger.warning(
                        f"Suspicious pattern detected in header {header_name}: {pattern.pattern}",
                        extra={'header_value': header_value, 'client_ip': self._get_client_ip(request)}
                    )
                    return True
        
        return False
    
    def _track_suspicious_activity(self, client_ip: str):
        """Track suspicious activity for rate limiting"""
        current_time = time.time()
        
        if client_ip not in self.suspicious_activity:
            self.suspicious_activity[client_ip] = []
        
        # Add current timestamp
        self.suspicious_activity[client_ip].append(current_time)
        
        # Clean old entries (older than 1 hour)
        self.suspicious_activity[client_ip] = [
            timestamp for timestamp in self.suspicious_activity[client_ip]
            if current_time - timestamp < 3600
        ]
        
        # If too many suspicious requests, add to blocklist
        if len(self.suspicious_activity[client_ip]) > 10:  # 10 suspicious requests in 1 hour
            self.blocked_ips.add(client_ip)
            logger.warning(f"IP {client_ip} added to blocklist due to suspicious activity")
    
    async def dispatch(self, request: Request, call_next) -> Response:
        client_ip = self._get_client_ip(request)
        
        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            logger.warning(f"Blocked IP attempted access: {client_ip}")
            return JSONResponse(
                status_code=403,
                content={
                    'error': 'Forbidden',
                    'message': 'Access denied'
                }
            )
        
        # Check if using allowlist
        if self.allowed_ips and client_ip not in self.allowed_ips:
            logger.warning(f"IP not in allowlist: {client_ip}")
            return JSONResponse(
                status_code=403,
                content={
                    'error': 'Forbidden',
                    'message': 'Access denied'
                }
            )
        
        # Check for suspicious patterns
        if self._is_suspicious_request(request):
            self._track_suspicious_activity(client_ip)
            return JSONResponse(
                status_code=400,
                content={
                    'error': 'BadRequest',
                    'message': 'Malformed request detected'
                }
            )
        
        return await call_next(request)


class CORSConfig:
    """Configuration for CORS middleware"""
    
    @staticmethod
    def get_development_config():
        """CORS configuration for development"""
        return {
            "allow_origins": [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:8080",
                os.getenv('FRONTEND_URL', '')
            ],
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
            "expose_headers": ["X-Correlation-ID", "X-Response-Time", "X-Cache"]
        }
    
    @staticmethod
    def get_production_config():
        """CORS configuration for production"""
        return {
            "allow_origins": [
                os.getenv('FRONTEND_URL', ''),
                os.getenv('ADMIN_URL', ''),
                # Add your production domains here
                # "https://yourdomain.com",
                # "https://api.yourdomain.com"
            ],
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            "allow_headers": [
                "Accept",
                "Accept-Language",
                "Content-Language",
                "Content-Type",
                "Authorization",
                "X-Correlation-ID",
                "X-Requested-With",
                "Origin",
                "Cache-Control",
                "Pragma"
            ],
            "expose_headers": [
                "X-Correlation-ID",
                "X-Response-Time",
                "X-Cache",
                "X-RateLimit-Limit-Minute",
                "X-RateLimit-Remaining-Minute"
            ]
        }


class SecurityManager:
    """Centralized security configuration manager"""
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.blocked_ips: Set[str] = set()
        self.allowed_ips: Optional[Set[str]] = None
    
    def add_blocked_ip(self, ip: str):
        """Add IP to blocklist"""
        self.blocked_ips.add(ip)
        logger.info(f"Added IP to blocklist: {ip}")
    
    def remove_blocked_ip(self, ip: str):
        """Remove IP from blocklist"""
        self.blocked_ips.discard(ip)
        logger.info(f"Removed IP from blocklist: {ip}")
    
    def set_allowed_ips(self, ips: List[str]):
        """Set allowed IPs (allowlist mode)"""
        self.allowed_ips = set(ips)
        logger.info(f"Set allowed IPs: {ips}")
    
    def clear_allowed_ips(self):
        """Clear allowlist (disable allowlist mode)"""
        self.allowed_ips = None
        logger.info("Cleared IP allowlist")
    
    def get_security_status(self) -> Dict:
        """Get current security configuration status"""
        return {
            "environment": self.environment,
            "blocked_ips_count": len(self.blocked_ips),
            "blocked_ips": list(self.blocked_ips) if len(self.blocked_ips) < 100 else "too_many_to_list",
            "allowlist_enabled": self.allowed_ips is not None,
            "allowed_ips_count": len(self.allowed_ips) if self.allowed_ips else 0,
            "allowed_ips": list(self.allowed_ips) if self.allowed_ips and len(self.allowed_ips) < 100 else None
        }


# Global security manager instance
security_manager = SecurityManager(environment=os.getenv("ENVIRONMENT", "development"))
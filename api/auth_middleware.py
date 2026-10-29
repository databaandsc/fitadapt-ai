import os
from typing import Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

try:
    from clerk_backend_api import Clerk
    from clerk_backend_api.security import authenticate_request, AuthenticateRequestOptions
    from clerk_backend_api.security.types import AuthStatus
    CLERK_AVAILABLE = True
except Exception:
    Clerk = None  # type: ignore
    authenticate_request = None  # type: ignore
    AuthenticateRequestOptions = None  # type: ignore
    AuthStatus = None  # type: ignore
    CLERK_AVAILABLE = False


PUBLIC_PATHS = {
    "/api/health",
    "/docs",
    "/openapi.json",
    "/redoc",
}


class ClerkAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, secret_key: str | None = None):
        super().__init__(app)
        self.secret_key = secret_key or os.getenv("CLERK_SECRET_KEY") or os.getenv("CLERK_BACKEND_API_KEY")

    async def dispatch(self, request: Request, call_next: Callable):
        path = request.url.path

        # Allow OPTIONS for CORS preflight
        if request.method == "OPTIONS":
            return await call_next(request)

        # Public paths
        if path in PUBLIC_PATHS or path.startswith("/docs") or path.startswith("/openapi"):
            return await call_next(request)

        # Only protect API routes
        if not path.startswith("/api/"):
            return await call_next(request)

        if not CLERK_AVAILABLE or not authenticate_request or not AuthenticateRequestOptions:
            # If Clerk SDK not available, in dev we might want to be strict
            # but to not break local dev without full setup, check for secret
            if not self.secret_key:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "No autorizado. Falta configuración de Clerk."},
                )
            # Fallback: try to be permissive if SDK missing? better to deny
            return JSONResponse(
                status_code=401,
                content={"detail": "No autorizado. Autenticación Clerk no disponible."},
            )

        try:
            clerk = Clerk(bearer_auth=self.secret_key) if self.secret_key else Clerk()
            request_state = authenticate_request(
                clerk,
                AuthenticateRequestOptions(
                    authorized_parties=[os.getenv("CLERK_AUTHORIZED_PARTY")] if os.getenv("CLERK_AUTHORIZED_PARTY") else None,
                ),
            )
            if request_state.status == AuthStatus.SIGNED_IN:
                request.state.user_id = getattr(request_state.payload, "sub", None) if request_state.payload else None
                request.state.session_id = getattr(request_state.payload, "sid", None) if request_state.payload else None
                return await call_next(request)
            else:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "No autorizado. Inicia sesión con Clerk."},
                )
        except Exception as e:
            return JSONResponse(
                status_code=401,
                content={"detail": "No autorizado."},
            )

import os
from typing import Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

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

        auth_header = request.headers.get("Authorization") or request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "No autorizado. Inicia sesión con Clerk."},
            )

        token = auth_header.split(" ", 1)[1]
        # Try to extract user_id from token without strict verification in dev
        try:
            import json
            import base64
            # JWT payload is base64url encoded
            parts = token.split(".")
            if len(parts) >= 2:
                payload_b64 = parts[1]
                # Add padding
                payload_b64 += "=" * (-len(payload_b64) % 4)
                payload = json.loads(base64.urlsafe_b64decode(payload_b64))
                request.state.user_id = payload.get("sub")
                request.state.session_id = payload.get("sid")
        except Exception:
            pass

        return await call_next(request)

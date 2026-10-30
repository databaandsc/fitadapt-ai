import os
import logging
from typing import Callable

import jwt                                              # (1)
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("fitadapt.auth")

PUBLIC_PATHS = {
    "/api/health",
    "/docs",
    "/openapi.json",
    "/redoc",
}

# (1) Endpoint de Clerk que devuelve las claves publicas para verificar los tokens JWT firmados por Clerk
CLERK_JWKS_URL = "https://api.clerk.com/v1/jwks"


def _unauthorized(detail: str) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": detail})


class ClerkAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, secret_key: str | None = None):
        super().__init__(app)
        self.secret_key = secret_key or os.getenv("CLERK_SECRET_KEY") or os.getenv("CLERK_BACKEND_API_KEY")
        self._jwks_client: jwt.PyJWKClient | None = None

    # (2) Cliente que descarga y cachea las claves públicas de Clerk
    def _get_jwks_client(self) -> jwt.PyJWKClient:
        if self._jwks_client is None:
            self._jwks_client = jwt.PyJWKClient(
                CLERK_JWKS_URL,
                cache_keys=True,
                                headers={
                    "Authorization": f"Bearer {self.secret_key}",
                    "User-Agent": "fitadaptai-backend",
                },

            )
        return self._jwks_client

    # (3) Verificación real del token
    def _verify(self, token: str) -> dict:
        signing_key = self._get_jwks_client().get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            leeway=5,
            options={"require": ["exp", "sub"]},
        )

    async def dispatch(self, request: Request, call_next: Callable):
        path = request.url.path

        if request.method == "OPTIONS":
            return await call_next(request)

        if path in PUBLIC_PATHS or path.startswith("/docs") or path.startswith("/openapi"):
            return await call_next(request)

        if not path.startswith("/api/"):
            return await call_next(request)

        auth_header = request.headers.get("Authorization") or request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return _unauthorized("No autorizado. Inicia sesión con Clerk.")

        # (4) Sin clave secreta se deniega el acceso, ya que no se puede verificar la sesión
        if not self.secret_key:
            logger.error("CLERK_SECRET_KEY no está configurada en el servidor")
            return _unauthorized("No autorizado. Falta configuración de Clerk en el servidor.")

        token = auth_header.split(" ", 1)[1].strip()

        # (5) Si la verificación falla, se devuelve un error 401. Si es exitosa, se añade la información del usuario a la request
        try:
            payload = await run_in_threadpool(self._verify, token)
        except jwt.PyJWKClientError:
            logger.exception("No se pudieron obtener las claves JWKS de Clerk")
            return _unauthorized("No autorizado. No se pudo validar la sesión con Clerk.")
        except jwt.InvalidTokenError:
            return _unauthorized("No autorizado. Sesión inválida o caducada.")

        # (6) El token es autentico
        request.state.user_id = payload.get("sub")
        request.state.session_id = payload.get("sid")
        return await call_next(request)

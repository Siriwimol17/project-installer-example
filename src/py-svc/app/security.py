"""Internal token and loopback Host validation."""

import secrets

from fastapi import HTTPException, Request, status


def validate_host(request: Request) -> None:
    host = request.headers.get("host", "")
    hostname = host.rsplit(":", 1)[0].strip("[]").lower()
    if hostname not in {"127.0.0.1", "localhost", "[::1]", "::1"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid host")


async def require_internal_token(request: Request) -> None:
    expected = request.app.state.settings.internal_token
    provided = request.headers.get("X-Internal-Token", "")
    if not secrets.compare_digest(provided.encode("utf-8"), expected.encode("utf-8")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")

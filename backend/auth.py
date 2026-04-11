import os
from functools import lru_cache
from typing import Any

import httpx
import jwt
from fastapi import Header, HTTPException

from backend.models import AuthenticatedUser

CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL", "")
CLERK_ISSUER = os.getenv("CLERK_ISSUER", "")


@lru_cache(maxsize=1)
def get_jwks() -> dict[str, Any]:
    if not CLERK_JWKS_URL:
        raise RuntimeError("CLERK_JWKS_URL is not configured.")

    response = httpx.get(CLERK_JWKS_URL, timeout=10)
    response.raise_for_status()
    return response.json()


def verify_clerk_token(token: str) -> dict[str, Any]:
    jwks = get_jwks()
    header = jwt.get_unverified_header(token)

    jwk = next(
        (candidate for candidate in jwks["keys"] if candidate["kid"] == header["kid"]),
        None,
    )
    if jwk is None:
        raise HTTPException(status_code=401, detail="Invalid token key.")

    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)

    return jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        issuer=CLERK_ISSUER or None,
        options={"verify_aud": False},
    )


async def get_current_user(
    authorization: str | None = Header(default=None),
) -> AuthenticatedUser:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token.")

    token = authorization.removeprefix("Bearer ").strip()
    claims = verify_clerk_token(token)

    return AuthenticatedUser(
        user_id=claims["sub"],
        email=claims.get("email") or claims.get("primary_email_address"),
    )

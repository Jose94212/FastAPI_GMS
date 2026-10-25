"""
Echo endpoint — a passive mirror for inspecting what reaches this service.

Unauthenticated ON PURPOSE: no auth dependency, so it never rejects a request.
It records and returns every header it received (Authorization included,
verbatim), plus method and query params. Used to see exactly what an upstream
caller (e.g. watsonx Orchestrate's tool runtime) forwards to a tool endpoint.

NOTE: because it reflects request headers back in the response body, keep this
disabled/removed in any real production deployment. It's a diagnostic tool.
"""
import logging

from fastapi import APIRouter, Request

logger = logging.getLogger(__name__)

router_echo = APIRouter(tags=["Echo"])


@router_echo.api_route("/echo", methods=["GET", "POST"])
async def echo(request: Request) -> dict:
    """
    Reflects the incoming request back to the caller. Returns the HTTP method,
    all request headers, and query parameters. No authentication is performed.
    """
    headers = dict(request.headers)
    auth_present = "authorization" in headers
    # Log whether an Authorization header arrived, but not its value.
    logger.info(f"/echo called — method={request.method} authorization_present={auth_present}")
    return {
        "message": "echo",
        "method": request.method,
        "authorization_present": auth_present,
        "headers": headers,
        "query": dict(request.query_params),
    }

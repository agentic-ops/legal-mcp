"""Legal Research & Paralegal MCP Server -- main entry point.

Initializes a FastMCP server, registers all tools, resources, and prompts,
and runs the selected transport. A module-level ``mcp`` instance is exposed
so the MCP Inspector / CLI can load it directly, e.g.::

    mcp dev main.py:mcp

Transport, host, and port can be configured via CLI flags or the
``MCP_TRANSPORT`` / ``HOST`` / ``PORT`` environment variables. The default
is SSE on 127.0.0.1:8000 to match the documented endpoints.
"""

from __future__ import annotations

import argparse
import logging
import os

from mcp.server.fastmcp import FastMCP

from demo_mode import DEMO_MODE_ENV, is_demo_mode
from prompts import register_all_prompts
from resources import register_all_resources
from tools import register_all_tools
from utils import audit, get_data_manager
from feature_flags import enabled_categories

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger("legal_mcp")

SERVER_NAME = "Legal Research & Paralegal MCP Server"


def server_instructions() -> str:
    """Describe the server without obscuring whether demo content is active."""

    base = (
        "Structured legal workflow tools for research, citation-format analysis, "
        "contract review, and brief scaffolding. Provides workflow augmentation, "
        "not legal advice."
    )
    if is_demo_mode():
        return (
            f"{base} DEMO DATA ONLY: bundled sample legal content is enabled and "
            "is not verified legal authority or user-supplied content."
        )
    return (
        f"{base} Production mode is active; bundled sample legal content is disabled."
    )


def create_server(host: str = "127.0.0.1", port: int = 8000) -> FastMCP:
    """Build and fully configure the FastMCP server instance."""

    server = FastMCP(
        SERVER_NAME,
        instructions=server_instructions(),
        host=host,
        port=port,
    )
    register_all_tools(server)
    register_all_resources(server)
    register_all_prompts(server)

    stats = get_data_manager().stats()
    categories = enabled_categories()
    logger.info("Registered legal data: %s", stats)
    logger.info("Enabled tool categories: %s", categories)
    if is_demo_mode():
        logger.warning(
            "DEMO MODE ENABLED via %s: fictional/sample legal content is active "
            "and must not be treated as verified authority.",
            DEMO_MODE_ENV,
        )
    else:
        logger.info(
            "Production mode active: bundled sample cases, statutes, and contracts "
            "were not loaded."
        )
    audit(
        "server_initialized",
        **stats,
        demo_mode=is_demo_mode(),
        enabled_categories=categories,
    )
    return server


# Module-level instance for `mcp dev main.py:mcp` and imports.
mcp = create_server(
    host=os.environ.get("HOST", "127.0.0.1"),
    port=int(os.environ.get("PORT", "8000")),
)


def main() -> None:
    """Parse arguments and run the Legal MCP Server."""

    parser = argparse.ArgumentParser(description=SERVER_NAME)
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default=os.environ.get("MCP_TRANSPORT", "sse"),
        help="Transport protocol (default: sse).",
    )
    parser.add_argument("--host", default=os.environ.get("HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8000")))
    args = parser.parse_args()

    mcp.settings.host = args.host
    mcp.settings.port = args.port

    logger.info(
        "Starting %s (transport=%s, host=%s, port=%s)",
        SERVER_NAME,
        args.transport,
        args.host,
        args.port,
    )
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()

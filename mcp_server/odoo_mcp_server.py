"""MCP server exposing a local Odoo instance's XML-RPC API to Claude.

Connection details are read from environment variables so no credential is
ever hardcoded in this file:
    ODOO_URL       e.g. http://localhost:8071
    ODOO_DB        e.g. school_crm
    ODOO_LOGIN     e.g. claude.mcp
    ODOO_API_KEY   the API key generated for that user (not a real password)
"""
import os
import xmlrpc.client

from mcp.server import MCPServer

ODOO_URL = os.environ["ODOO_URL"]
ODOO_DB = os.environ["ODOO_DB"]
ODOO_LOGIN = os.environ["ODOO_LOGIN"]
ODOO_API_KEY = os.environ["ODOO_API_KEY"]

_common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
_uid = _common.authenticate(ODOO_DB, ODOO_LOGIN, ODOO_API_KEY, {})
if not _uid:
    raise RuntimeError(
        f"Failed to authenticate to Odoo at {ODOO_URL} as {ODOO_LOGIN!r}. "
        "Check ODOO_URL/ODOO_DB/ODOO_LOGIN/ODOO_API_KEY."
    )
_models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")


def _execute(model, method, *args, **kwargs):
    return _models.execute_kw(ODOO_DB, _uid, ODOO_API_KEY, model, method, list(args), kwargs)


mcp = MCPServer("Odoo School CRM")


@mcp.tool()
def odoo_search_read(model: str, domain: list = [], fields: list = [], limit: int = 80,
                      order: str = "") -> list:
    """Search and read records from an Odoo model.

    :param model: technical model name, e.g. "edu.student"
    :param domain: Odoo domain filter, e.g. [["state", "=", "active"]]
    :param fields: list of field names to return; empty returns all stored fields
    :param limit: max number of records to return
    :param order: sort spec, e.g. "name asc"
    """
    kwargs = {"limit": limit}
    if fields:
        kwargs["fields"] = fields
    if order:
        kwargs["order"] = order
    return _execute(model, "search_read", domain, **kwargs)


@mcp.tool()
def odoo_search_count(model: str, domain: list = []) -> int:
    """Count records on an Odoo model matching a domain filter."""
    return _execute(model, "search_count", domain)


@mcp.tool()
def odoo_create(model: str, values: dict) -> int:
    """Create a single record on an Odoo model. Returns the new record's id."""
    return _execute(model, "create", values)


@mcp.tool()
def odoo_write(model: str, ids: list, values: dict) -> bool:
    """Update one or more existing records on an Odoo model."""
    return _execute(model, "write", ids, values)


@mcp.tool()
def odoo_unlink(model: str, ids: list) -> bool:
    """Permanently delete one or more records. There is no undo -- use with care."""
    return _execute(model, "unlink", ids)


@mcp.tool()
def odoo_call_method(model: str, method: str, ids: list = [], args: list = [],
                      kwargs: dict = {}) -> object:
    """Call any model method (e.g. an action button like 'action_confirm') on
    a set of record ids. Runs under the same permissions as the connected
    Odoo user -- Odoo's own access rights and record rules still apply.
    """
    return _execute(model, method, ids, *args, **kwargs)


@mcp.tool()
def odoo_fields_get(model: str) -> dict:
    """List a model's fields (name, type, string label, required) so you know
    what's available before calling search_read/create/write."""
    fields_info = _execute(model, "fields_get", [], {"attributes": ["string", "type", "required", "relation"]})
    return fields_info


if __name__ == "__main__":
    mcp.run()

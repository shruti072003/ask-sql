import re
import logging

logger = logging.getLogger(__name__)

# Patterns that indicate a potentially destructive or mutating SQL statement
_DANGEROUS_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\bINSERT\b", re.IGNORECASE), "INSERT statement detected — would modify data"),
    (re.compile(r"\bUPDATE\b", re.IGNORECASE), "UPDATE statement detected — would modify data"),
    (re.compile(r"\bDELETE\b", re.IGNORECASE), "DELETE statement detected — would remove data"),
    (re.compile(r"\bDROP\b", re.IGNORECASE), "DROP statement detected — would destroy a table or database"),
    (re.compile(r"\bTRUNCATE\b", re.IGNORECASE), "TRUNCATE statement detected — would erase all rows"),
    (re.compile(r"\bALTER\b", re.IGNORECASE), "ALTER statement detected — would modify schema"),
    (re.compile(r"\bCREATE\b", re.IGNORECASE), "CREATE statement detected — would modify schema"),
    (re.compile(r"\bGRANT\b", re.IGNORECASE), "GRANT statement detected — would change permissions"),
    (re.compile(r"\bREVOKE\b", re.IGNORECASE), "REVOKE statement detected — would change permissions"),
    (re.compile(r";\s*--", re.IGNORECASE), "Possible SQL injection comment terminator detected"),
]


def check_sql(sql: str) -> dict:
    """
    Inspect *sql* for dangerous or write operations.

    Returns:
        {"requires_approval": True,  "reason": "<human-readable explanation>"}
        {"requires_approval": False}

    Never raises — returns a safe default if sql is empty or None.
    """
    if not sql or not sql.strip():
        return {"requires_approval": False}

    for pattern, reason in _DANGEROUS_PATTERNS:
        if pattern.search(sql):
            logger.warning("HITL guard flagged SQL. Reason: %s", reason)
            return {"requires_approval": True, "reason": reason}

    return {"requires_approval": False}

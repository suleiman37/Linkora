from urllib.parse import urlsplit, urlunsplit


def normalize_url(value: str) -> str:
    parsed = urlsplit(value)
    scheme = parsed.scheme.lower()
    hostname = (parsed.hostname or "").lower()

    if ":" in hostname and not hostname.startswith("["):
        hostname = f"[{hostname}]"

    port = parsed.port
    default_port = (scheme == "http" and port == 80) or (
        scheme == "https" and port == 443
    )
    netloc = hostname if default_port or port is None else f"{hostname}:{port}"

    return urlunsplit((scheme, netloc, parsed.path, parsed.query, parsed.fragment))
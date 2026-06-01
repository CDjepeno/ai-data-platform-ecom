import httpx

timeout = httpx.Timeout(
    connect=10.0,
    read=None,
    write=30.0,
    pool=30.0,
)

limits = httpx.Limits(
    max_connections=100,
    max_keepalive_connections=20,
)

client = httpx.AsyncClient(
    timeout=timeout,
    limits=limits,
)
from aiohttp import ClientSession, TCPConnector, ClientTimeout, CookieJar
import contextlib
from . import amazon, flipkart, myntra

ADAPTER_LIST = [amazon, flipkart, myntra]

@contextlib.asynccontextmanager
async def get_client_session():
    conn = TCPConnector(limit=10, ssl=False)
    timeout = ClientTimeout(total=15)
    jar = CookieJar()
    async with ClientSession(connector=conn, timeout=timeout, cookie_jar=jar) as session:
        yield session

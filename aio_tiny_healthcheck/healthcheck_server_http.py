from aiohttp import web
import asyncio
from aio_tiny_healthcheck import AioTinyHealthcheck


__all__ = ['HealthcheckServerHttp']


class HealthcheckServerHttp:
    """
    Async server for running healthcheck in case
    when you do not want to block execution flow by web-server
    """
    def __init__(
        self,
        healthcheck_provider: AioTinyHealthcheck,
        host: str = '0.0.0.0',
        path: str = '/healthcheck',
        port: int = 8000
    ):
        """
        :param healthcheck_provider: AioTinyHealthcheck instance
        :param host: listened host
        :param path: URL path to healthcheck
        :param port: port
        """
        self._healthcheck_provider = healthcheck_provider
        self._host = host
        self._port = port
        self._path = path
        self._running = False

    async def _handler(self, request):
        path = request.path.rstrip('/')

        if path == self._path:
            response = await self._healthcheck_provider.aiohttp_handler()
        else:
            response = web.Response(body='404 Not Found', status=404)

        return response

    async def run(self):
        """
        Run healthcheck http-server.
        You can run this method concurrently.
        Example: ```asyncio.create_task(hc_server.run())```
        """
        if self._running is False:
            self._running = True

            server = web.Server(self._handler)
            runner = web.ServerRunner(server)
            await runner.setup()
            site = web.TCPSite(runner, self._host, self._port)
            await site.start()

            while self._running is True:
                await asyncio.sleep(1)
        else:
            raise RuntimeError('Can not run healthcheck server twice')

    def stop(self):
        """
        Stop running the server
        """
        self._running = False

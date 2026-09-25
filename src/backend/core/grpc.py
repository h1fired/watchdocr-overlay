import grpc


class GRPCServer:
    def __init__(self, host: str):
        self._host = host
        self._server = None
        self._is_alive = False
        self._services = []

    async def run(self):
        if self._is_alive:
            return
        self._server = grpc.aio.server()
        self._server.add_insecure_port(self._host)
        await self._server.start()
        self._is_alive = True

    async def stop(self):
        if not self._is_alive:
            return
        await self._server.stop()
        self._is_alive = False

    async def wait_for_termination(self):
        if not self._is_alive:
            return
        await self._server.wait_for_termination()

    def register_service(self, service: 'GRPCService'):
        self._services.append(service)


class UseDispatcher:
    pass


class GRPCService:
    def __init__(self, dispatcher: UseDispatcher):
        self._dispatcher = dispatcher

    @property
    def dispatcher(self):
        return self._dispatcher

    def add_to_server(self, server: GRPCServer):
        raise NotImplementedError

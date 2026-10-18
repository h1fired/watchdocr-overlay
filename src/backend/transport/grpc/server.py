import grpc
from grpc_reflection.v1alpha import reflection


class GRPCServer:
    def __init__(
        self,
        host: str,
        enable_reflection: bool = False,
        interceptors: list[grpc.aio.ServerInterceptor] = [],
    ):
        self._host = host
        self._enable_reflection = enable_reflection
        self._interceptors = interceptors
        self._server = None
        self._is_alive = False
        self._services = []

    async def run(self):
        if self._is_alive:
            return

        self._server = grpc.aio.server(interceptors=self._interceptors)
        self._server.add_insecure_port(self._host)

        # Load services
        for service in self._services:
            service.add_to_server(self._server)

        if self._enable_reflection:
            self._enable_server_reflection()

        await self._server.start()

    def _enable_server_reflection(self):
        service_names = [
            name
            for service in self._services
            for name in service.service_names()
        ]
        service_names.append(reflection.SERVICE_NAME)
        reflection.enable_server_reflection(service_names, self._server)
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

    def service_names(self) -> list[str]:
        recorder = _ServiceNameRecorder()
        self.add_to_server(recorder)
        return recorder.names


class _ServiceNameRecorder:
    """Captures the gRPC service names a servicer registers, without a server.

    Generated ``add_*_to_server`` helpers register their handlers through
    ``add_generic_rpc_handlers``; each handler exposes its full service name,
    so any service can report its names without per-service code.
    """

    def __init__(self):
        self.names = []

    def add_generic_rpc_handlers(self, handlers):
        for handler in handlers:
            self.names.append(handler.service_name())

    def add_registered_method_handlers(self, *args, **kwargs):
        pass

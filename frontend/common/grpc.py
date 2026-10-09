import grpc


class GRPCClient:
    def __init__(self, host: str):
        self._host = host
        self._channel = None
        self._is_alive = False
        self._stubs = []

    async def run(self):
        if self._is_alive:
            return

        self._channel = grpc.aio.insecure_channel(self._host)

        # Load stubs
        for stub in self._stubs:
            stub.add_to_channel(self._channel)

        await self._channel.channel_ready()
        self._is_alive = True

    async def stop(self):
        if not self._is_alive:
            return
        await self._channel.close()
        self._is_alive = False

    def register_stub(self, service: 'GRPCStub'):
        self._stubs.append(service)


class GRPCStub:
    def add_to_channel(self, channel: grpc.aio.Channel):
        raise NotImplementedError

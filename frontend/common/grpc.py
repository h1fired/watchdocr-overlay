import grpc
from typing import TypeVar


T = TypeVar('T')

_CHANNEL_OPTIONS = (
    ('grpc.initial_reconnect_backoff_ms', 500),
    ('grpc.min_reconnect_backoff_ms', 500),
    ('grpc.max_reconnect_backoff_ms', 5000),
    ('grpc.keepalive_time_ms', 10000),
    ('grpc.keepalive_timeout_ms', 5000),
    ('grpc.keepalive_permit_without_calls', 1),
)


class GRPCClient:
    def __init__(self, host: str):
        self._host = host
        self._channel = None
        self._is_alive = False
        self._stubs: dict[type[GRPCStub], GRPCStub] = {}

    async def start(self):
        if self._is_alive:
            return

        self._channel = grpc.aio.insecure_channel(
            target=self._host,
            options=_CHANNEL_OPTIONS
        )

        # Load stubs
        for stub in self._stubs.values():
            stub.add_to_channel(self._channel)

        await self._channel.channel_ready()
        self._is_alive = True

    async def stop(self):
        if not self._is_alive:
            return
        await self._channel.close()
        self._is_alive = False

    def register_stub(self, service: 'GRPCStub'):
        self._stubs[type(service)] = service

    def get_stub(self, stub: type[T]) -> T:
        return self._stubs[stub]


class GRPCStub:
    def add_to_channel(self, channel: grpc.aio.Channel):
        raise NotImplementedError

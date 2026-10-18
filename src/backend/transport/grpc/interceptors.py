import asyncio
import grpc
from typing import Any, Callable
from grpc_interceptor import AsyncServerInterceptor
from grpc_interceptor.exceptions import GrpcException
from src.backend.common.utils.logging import log


LOG_TITLE = 'GRPC_INTERCEPTOR'


class ExceptionToStatusInterceptor(AsyncServerInterceptor):
    async def intercept(
        self,
        method: Callable,
        request_or_iterator: Any,
        context: grpc.aio.ServicerContext,
        method_name: str,
    ) -> Any:
        try:
            result = method(request_or_iterator, context)
            if hasattr(result, '__aiter__'):
                return self._wrap_stream(result, context, method_name)
            return await result
        except asyncio.CancelledError:
            raise
        except Exception as e:
            await self._abort(e, context, method_name)

    async def _wrap_stream(self, iterator, context, method_name):
        try:
            async for item in iterator:
                yield item
        except asyncio.CancelledError:
            raise
        except Exception as e:
            await self._abort(e, context, method_name)

    async def _abort(self, e: Exception, context, method_name: str):
        if isinstance(e, grpc.aio.AbortError):
            raise e
        if isinstance(e, GrpcException):
            log.warning(
                'gRPC error in %s: %s',
                method_name,
                e.details,
                extra={'title': LOG_TITLE}
            )
            await context.abort(e.status_code, e.details or '')

        log.exception(
            'Unhandled error in %s',
            method_name,
            extra={'title': LOG_TITLE}
        )
        await context.abort(grpc.StatusCode.INTERNAL, 'Internal server error')

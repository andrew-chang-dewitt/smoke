r"""
A couple of simple pub sub utilities for concurrent event handling.
"""

from asyncio import gather
from threading import Thread
from typing import Awaitable, Callable, Generic, List, Self, TypeVar


T = TypeVar('T')
R = TypeVar('R')


class ChannelSPMCAsync(Generic[T, R]):
    """An async event channel for registering subscribers to a publisher."""

    # FIXME: maybe T could be a generic list of type arguments instead of
    # just one argument
    _subs: List[Callable[[T], Awaitable[R]]]

    def __init__(self) -> None:
        self._subs = []

    def sub(self, sub: Callable[[T], Awaitable[R]]) -> Self:
        """Subscribe a function to the channel."""
        self._subs.append(sub)

        return self

    async def pub(self, arg: T) -> None:
        """Publish an event with the given arg."""
        futures = [sub(arg) for sub in self._subs]
        await gather(*futures)


class ChannelSPMCThreaded(Generic[T, R]):
    """A threaded event channel for registering subscribers to a publisher."""

    _subs: List[Callable[[T], R]]

    def __init__(self) -> None:
        self._subs = []

    def sub(self, sub: Callable[[T], R]) -> Self:
        """Subscribe a function to the channel."""
        self._subs.append(sub)

        return self

    def pub(self, arg: T) -> List[Thread]:
        """Publish an event with the given arg."""
        threads = []

        for sub in self._subs:
            threads.append(Thread(
                target=sub,
                args=[arg],
            ))

        for thread in threads:
            thread.start()

        return threads

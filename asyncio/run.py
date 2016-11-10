"""asyncio.run() function."""

__all__ = ['run']

import threading

from . import coroutines
from . import events


def run(coro, *, debug=False):
    """Run a coroutine.

    This function runs the passed coroutine, taking care of
    managing the asyncio event loop and finalizing asynchronous
    generators.

    This function must be called from the main thread, and it
    cannot be called when another asyncio event loop is running.

    If debug is True, the event loop will be run in debug mode.

    This function should be used as a main entry point for
    asyncio programs, and should not be used to call asynchronous
    APIs.

    Example::

        import asyncio

        async def main():
            await asyncio.sleep(1)
            print('hello')

        asyncio.run(main())
    """
    if events._get_running_loop() is not None:
        raise RuntimeError(
            "asyncio.run() cannot be called from a running event loop")
    if not isinstance(threading.current_thread(), threading._MainThread):
        raise RuntimeError(
            "asyncio.run() must be called from the main thread")
    if not coroutines.iscoroutine(coro):
        raise ValueError("a coroutine was expected, got {!r}".format(coro))

    loop = events.new_event_loop()
    try:
        events.set_event_loop(loop)

        if debug:
            loop.set_debug(True)

        result = loop.run_until_complete(coro)

        try:
            # `shutdown_asyncgens` was added in Python 3.6; not all
            # event loops might support it.
            shutdown_asyncgens = loop.shutdown_asyncgens
        except AttributeError:
            pass
        else:
            loop.run_until_complete(shutdown_asyncgens())

        return result

    finally:
        events.set_event_loop(None)
        loop.close()

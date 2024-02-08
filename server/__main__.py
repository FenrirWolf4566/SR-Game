import signal
import asyncio

from . import server

async def shutdown(sig):
    print(f"Received signal '{signal.strsignal(sig)}', shutting down...")
    server.stop()

for sig in (signal.SIGTERM, signal.SIGINT):
    signal.signal(sig, lambda s, _: asyncio.create_task(shutdown(s)))

async def main():
    await server.serve()

asyncio.run(main())
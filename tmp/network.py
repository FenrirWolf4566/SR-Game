import asyncio
import socket
from typing import Callable

Socket = socket.socket
Address = tuple[str, int]

class Network:
    def __init__(self, sock: Socket, on_receive: Callable[[bytes], None], on_remote_close: Callable[[], None]):
        self.sock = sock
        self.on_receive = on_receive
        self.on_remote_close = on_remote_close
        self.__task = None
    
    def start(self, cleanup: Callable[[None], None] = None):
        self.__task = asyncio.create_task(self.__process())
        if cleanup:
            self.__task.add_done_callback(cleanup)

    def stop(self):
        self.__task.cancel()
        self.sock.close()

    async def send(self, data: bytes):
        loop = asyncio.get_event_loop()
        await loop.sock_sendall(self.sock, data)
    
    async def __process(self):
        loop = asyncio.get_event_loop()
        run = True
        while run:
            try:
                data = await loop.sock_recv(self.sock, 1024)
                if data:
                    self.on_receive(data)
                else:
                    run = False
                    self.on_remote_close()
            except asyncio.CancelledError:
                run = False

def create(addr: Address, on_receive: Callable[[bytes], None], on_remote_close: Callable[[], None]) -> Network:
    sock = Socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(addr)
    sock.setblocking(False)
    return Network(sock, on_receive, on_remote_close)

def use_existing(sock: Socket, on_receive: Callable[[bytes], None], on_remote_close: Callable[[], None]) -> Network:
    return Network(sock, on_receive, on_remote_close)
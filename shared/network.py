import asyncio
import socket
from typing import Callable

Socket = socket.socket
Address = tuple[str, int]

class Network:
    def __init__(self, sock: Socket, on_receive, on_remote_close: Callable[[], None]):
        self.sock = sock
        self.on_receive = on_receive
        self.on_remote_close = on_remote_close
        self.__task = None
    
    def get_raw_id(self):
        sock_infos = self.sock.getpeername()
        return sock_infos[0] + '.' + str(sock_infos[1])

    def start(self):
        self.__task = asyncio.create_task(self.__process())

    def stop(self):
        self.__task.cancel()
        self.sock.close()

    async def send(self, data: bytes):
        loop = asyncio.get_running_loop()
        await loop.sock_sendall(self.sock, data)
    
    async def __process(self):
        loop = asyncio.get_running_loop()
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
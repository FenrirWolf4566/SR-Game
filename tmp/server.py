import asyncio
import signal
import socket

Addr = tuple[str, int]
Sock = socket.socket

HOST_ADDR = Addr(('192.168.1.31', 12345))

server = Sock(socket.AF_INET, socket.SOCK_STREAM)
server.bind(HOST_ADDR)
server.listen()
print(f'Listening on {HOST_ADDR}')
server.setblocking(False)


clients: dict[Addr, Sock] = {}

async def process_client(client: Sock, addr: Addr):
    loop = asyncio.get_event_loop()
    clients[addr] = client
    run = True
    while run:
        try:
            data = await loop.sock_recv(client, 1024)
            if data:
                print(f'Received {data} from {addr}')
            else:
                run = False
                print(f'Closing {addr}')
        except asyncio.CancelledError:
            run = False
        except ConnectionResetError:
            run = False
            print(f'Connexion closed by {addr}')
    del clients[addr]
    client.close()

async def send_to_all_periodically():
    loop = asyncio.get_event_loop()
    run = True
    while run:
        try:
            await asyncio.sleep(2)
            for client in clients.values():
                await loop.sock_sendall(client, b'Hey')
                print(f'Sent to {client.getpeername()}')
        except asyncio.CancelledError:
            run = False

async def main():
    loop = asyncio.get_event_loop()
    loop.create_task(send_to_all_periodically())
    run = True
    while run:
        try:
            client, addr = await loop.sock_accept(server)
            print(f'Accepted connection from {addr}')
            loop.create_task(process_client(client, addr))
        except asyncio.CancelledError:
            run = False

def sighandle(sig, frame):
    print('Cancelling tasks')
    tasks = asyncio.all_tasks()
    for task in tasks:
        task.cancel()

for sig in (signal.SIGINT, signal.SIGTERM):
    signal.signal(sig, sighandle)

asyncio.run(main())
server.close()

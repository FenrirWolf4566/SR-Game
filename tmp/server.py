import asyncio
import network
import signal
import socket

HOST_ADDR = ('127.0.0.1', 12345)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(HOST_ADDR)
server.listen()
print(f'Listening on {HOST_ADDR}')
server.setblocking(False)

nws: dict[network.Address, network.Network] = {}

list_of_input_msgs = [(42,10,1),(42,10,1),(42,10,1)]

def on_receive(data):
    print(f'Received {str(data)}')

def on_remote_close():
    print('Connection closed by client')

async def broadcast_update():
    run = True
    while run:
        try:
            await asyncio.sleep(2)
            for nw in nws.values():
                print("sending")
                await nw.send(bytes(list_of_input_msgs))
        except asyncio.CancelledError:
            run = False

async def main():
    loop = asyncio.get_event_loop()
    loop.create_task(broadcast_update())
    run = True
    while run:
        try:
            conn, addr = await loop.sock_accept(server)
            print(f'Accepted connection from {addr}')
            nw = network.use_existing(conn, on_receive, on_remote_close)
            nws[addr] = nw
            nw.start(lambda _: nws.pop(addr))

        except asyncio.CancelledError:
            run = False
    for nw in nws.values():
        nw.stop()
    server.close()

async def shutdown(sig):
    print(f"Received signal '{signal.strsignal(sig)}', exiting...")
    for task in asyncio.all_tasks():
        task.cancel()
    

for sig in (signal.SIGTERM, signal.SIGINT):
    signal.signal(sig, lambda s, _: asyncio.create_task(shutdown(s)))

asyncio.run(main())

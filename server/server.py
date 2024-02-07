import asyncio
from collections import namedtuple
import socket

from shared import network

HOST_ADDR = ('localhost', 12345)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(HOST_ADDR)
server.listen()
print(f'Listening on {HOST_ADDR}')
server.setblocking(False)

tasks: list[asyncio.Task] = []

networks: dict[network.Address, network.Network] = {}

plate = [(1,1,1),(2,2,2),(3,3,3)]

def on_receive(data):
    print(f'Received {data}')

def on_remote_close():
    print('Connection closed by client')

async def send_to_user(network):
    try:
        data_list = [str(tpl) for tpl in plate]
        data = '|'.join(data_list)
        await network.send(bytes(data, encoding='utf-8'))
    except Exception as e:
        print(f"FAILED WITH EXCEPTION : {e}")

async def broadcast_update():
    run = True
    while run:
        try:
            await asyncio.sleep(2)
            for nw in networks.values():
                await send_to_user(nw)
        except asyncio.CancelledError:
            run = False

async def accept():
    loop = asyncio.get_running_loop()
    run = True
    while run:
        try:
            conn, addr = await loop.sock_accept(server)
            print(f'Accepted connection from {addr}')
            nw = network.use_existing(conn, on_receive, on_remote_close)
            networks[addr] = nw
            nw.start(lambda _, addr=addr: networks.pop(addr))
        except asyncio.CancelledError:
            run = False

async def serve():
    loop = asyncio.get_running_loop()
    tasks.append(loop.create_task(broadcast_update()))
    tasks.append(loop.create_task(accept()))
    await asyncio.wait(tasks)

def stop():
    for task in tasks:
        task.cancel()
    for nw in networks.values():
        nw.stop()
    server.close()
